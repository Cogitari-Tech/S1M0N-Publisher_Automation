"""
Robô de Conteúdo Automatizado - Versão 5.0 (FINAL)
- ✅ Trava de Segurança (Hard Limit)
- ✅ SEO Injection (Yoast/RankMath)
- ✅ Configurações Dinâmicas via Banco de Dados
- ✅ Cache Inteligente v2
"""
import base64
import json
import time
import os
import hashlib
import re
import warnings
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from functools import lru_cache
import logging
from logging.handlers import RotatingFileHandler

# Imports de terceiros
from dotenv import load_dotenv
import feedparser
import requests
from newspaper import Article
import schedule
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.generativeai as genai

# Imports locais
from approval_system import save_for_approval
from prompt_optimizer import PromptOptimizer
from sources_manager import AdvancedSourcesManager
from cache_manager import CacheManager
from system_optimizer import SystemOptimizer
from database_models import (
    Base, 
    PublishedArticle, 
    RateLimitLog, 
    APIUsageLog,
    SystemSettings, # 🆕 Importado para configs dinâmicas
    get_database_session
)

load_dotenv()
warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================
# CONFIGURAÇÃO DE LOGGING
# ============================================
def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    file_handler = RotatingFileHandler('robot.log', maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logging()

@dataclass
class ArticleData:
    url: str
    title: str
    source: str
    content: str
    published_date: datetime
    hash: str

# ============================================
# CONTENT ROBOT CLASS (v5.0)
# ============================================
class ContentRobot:
    def __init__(self, static_config: Dict):
        self.static_config = static_config # Configurações imutáveis (ex: lista de RSS)
        self.ai_client = None
        self.session = None
        self.category_map = {}
        self.tag_map = {}
        
        # Gerenciadores
        self.sources_manager = AdvancedSourcesManager()
        self.prompt_optimizer = PromptOptimizer()
        self.cache_manager = CacheManager(ttl_days=7)
        self.system_optimizer = SystemOptimizer()
        
        self._init_database()
        
        # 🆕 Inicialização tardia de APIs (lê do banco primeiro)
        self._init_gemini() 
        self._validate_wordpress_credentials()
        self._load_wordpress_metadata()
        
        self.use_cache = True
        self.use_ab_testing = False
        
        logger.info("🤖 ContentRobot v5.0 inicializado (Engine Dinâmica)")

    def _init_database(self):
        try:
            self.session = get_database_session()
            logger.info("✅ Banco de dados conectado")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar banco: {e}")
            raise

    # 🆕 MÉTODO CENTRAL DE CONFIGURAÇÃO DINÂMICA
    def _get_setting(self, key: str, default: str = None) -> str:
        """Busca configuração no DB; fallback para .env ou default"""
        try:
            # 1. Tenta DB
            setting = self.session.query(SystemSettings).filter_by(key=key).first()
            if setting and setting.value:
                return setting.value
            
            # 2. Tenta .env (apenas para fallback inicial)
            env_val = os.getenv(key.upper())
            if env_val:
                return env_val
            
            # 3. Default
            return default
        except Exception:
            return default

    def _init_gemini(self):
        # 🆕 Lê chave do banco ou env
        api_key = os.getenv('GOOGLE_API_KEY') 
        
        if not api_key:
            logger.error("❌ GOOGLE_API_KEY não encontrada (Nem DB nem ENV)")
            return
        
        try:
            genai.configure(api_key=api_key)
            self.ai_client = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("✅ Gemini AI inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Gemini: {e}")

    def fetch_youtube_video(self, title: str, keywords: List[str]) -> Optional[str]:
        if self.use_cache:
            cached_url = self.cache_manager.get_cached_youtube(title, keywords)
            if cached_url: return cached_url

        # 🆕 Lê chave do banco
        youtube_api_key = self._get_setting('youtube_api_key')
        
        if not youtube_api_key:
            return None
        
        try:
            self._rate_limit('youtube', 2.0)
            query = f"{title} {' '.join(keywords[:3])}"
            
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={'part': 'snippet', 'q': query, 'type': 'video', 'maxResults': 1, 'key': youtube_api_key, 'relevanceLanguage': 'pt'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    vid = data['items'][0]['id']['videoId']
                    url = f"https://www.youtube.com/watch?v={vid}"
                    if self.use_cache:
                        self.cache_manager.save_cached_youtube(title, keywords, url, data['items'][0]['snippet']['title'])
                    return url
        except Exception as e:
            logger.error(f"❌ Erro YouTube: {e}")
        return None

    def upload_image_to_wordpress(self, image_path: str) -> Optional[int]:
        # 🆕 Credenciais do Banco
        wp_url = self._get_setting('wordpress_url')
        wp_user = self._get_setting('wordpress_username')
        wp_pass = self._get_setting('wordpress_password')
        
        if not all([wp_url, wp_user, wp_pass, image_path]): return None
        
        try:
            with open(image_path, 'rb') as img:
                files = {'file': (os.path.basename(image_path), img, 'image/png')}
                res = requests.post(f'{wp_url}/wp-json/wp/v2/media', auth=(wp_user, wp_pass), files=files, timeout=60)
                if res.status_code == 201: return res.json()['id']
        except Exception as e:
            logger.error(f"❌ Erro upload imagem: {e}")
        return None

    def _validate_wordpress_credentials(self):
        url = self._get_setting('wordpress_url')
        user = self._get_setting('wordpress_username')
        pwd = self._get_setting('wordpress_password')
        
        if not all([url, user, pwd]):
            logger.warning("⚠️ Credenciais WP incompletas no banco. Modo manual forçado.")
            return False
            
        try:
            res = requests.get(f'{url}/wp-json/wp/v2/users/me', auth=(user, pwd), timeout=10)
            if res.status_code == 200:
                logger.info(f"✅ WordPress conectado: {res.json().get('name')}")
                return True
        except Exception as e:
            logger.error(f"❌ Erro validação WP: {e}")
        return False

    def _load_wordpress_metadata(self):
        url = self._get_setting('wordpress_url')
        user = self._get_setting('wordpress_username')
        pwd = self._get_setting('wordpress_password')
        
        if not all([url, user, pwd]): return
        
        try:
            cats = requests.get(f'{url}/wp-json/wp/v2/categories?per_page=100', auth=(user, pwd)).json()
            self.category_map = {c['name']: c['id'] for c in cats} if isinstance(cats, list) else {}
            
            tags = requests.get(f'{url}/wp-json/wp/v2/tags?per_page=100', auth=(user, pwd)).json()
            self.tag_map = {t['name']: t['id'] for t in tags} if isinstance(tags, list) else {}
        except Exception:
            pass

    def _rate_limit(self, service: str, min_interval: float = 2.0):
        try:
            log = self.session.query(RateLimitLog).filter_by(service=service).first()
            if log:
                elapsed = (datetime.now() - log.last_request).total_seconds()
                if elapsed < min_interval: time.sleep(min_interval - elapsed)
                log.last_request = datetime.now()
            else:
                self.session.add(RateLimitLog(service=service, last_request=datetime.now()))
            self.session.commit()
        except:
            time.sleep(min_interval)

    def is_duplicate(self, article_hash: str) -> bool:
        return self.session.query(PublishedArticle).filter_by(hash=article_hash).first() is not None

    def fetch_rss_feeds(self) -> List[ArticleData]:
        articles = []
        # Mantém feeds estáticos do código ou poderia vir do banco também
        feeds = self.static_config.get('rss_feeds', [])
        
        for feed_url in feeds:
            try:
                self._rate_limit('rss', 1.0)
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    h = hashlib.md5(entry.link.encode()).hexdigest()
                    if not self.is_duplicate(h):
                        articles.append(ArticleData(url=entry.link, title=entry.title, source=feed.feed.get('title', 'RSS'), content='', published_date=datetime.now(), hash=h))
            except Exception: pass
        return articles

    def extract_article_content(self, article: ArticleData) -> Optional[ArticleData]:
        try:
            self._rate_limit('extraction', 1.0)
            a = Article(article.url)
            a.download()
            a.parse()
            article.content = a.text
            return article if len(a.text) > 150 else None
        except: return None

    def process_with_gemini(self, article: ArticleData) -> Optional[Dict]:
        if self.use_cache:
            cached = self.cache_manager.get_cached_content(article.title, article.content, 'gemini')
            if cached: return cached

        prompt_template = """
        Atue como jornalista expert. Reescreva o artigo abaixo em PT-BR.
        Regras: HTML (h2, h3), Otimizado SEO, Tom profissional.
        Original: {title}
        Conteúdo: {content}
        
        JSON OBRIGATÓRIO:
        {{
            "titulo": "...", "meta_description": "...", 
            "conteudo_completo": "...", "palavras_chave": ["..."],
            "categoria": "Notícias", "qualidade_score": 85,
            "originalidade_score": 90
        }}
        """
        
        try:
            self._rate_limit('gemini', 2.0)
            prompt = prompt_template.format(title=article.title, content=article.content[:4000])
            response = self.ai_client.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            result = json.loads(text)
            
            # Validação mínima
            if 'titulo' in result and self.use_cache:
                self.cache_manager.save_cached_content(article.title, article.content, 'gemini', result)
            
            return result
        except Exception as e:
            logger.error(f"❌ Erro Gemini: {e}")
            return None

    def generate_image_stable_diffusion(self, title: str) -> Optional[str]:
        # 🆕 Lê estilo do banco
        style_prompt = self._get_setting('image_prompt_style', 'Editorial illustration')
        full_prompt = f"{style_prompt}: {title}"
        
        if self.use_cache:
            c = self.cache_manager.get_cached_image(full_prompt)
            if c: return c
            
        api_key = self._get_setting('stability_api_key')
        if not api_key: return self._use_placeholder(title)
        
        try:
            self._rate_limit('stability', 5.0)
            res = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"text_prompts": [{"text": full_prompt, "weight": 1}], "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1},
                timeout=60
            )
            if res.status_code == 200:
                data = res.json()
                path = f"images/gen_{int(time.time())}.png"
                os.makedirs('images', exist_ok=True)
                with open(path, 'wb') as f: f.write(base64.b64decode(data['artifacts'][0]['base64']))
                if self.use_cache: self.cache_manager.save_cached_image(full_prompt, path)
                return path
        except Exception: pass
        return self._use_placeholder(title)

    def _use_placeholder(self, title: str) -> str:
        # Lógica simplificada de placeholder
        return "images/placeholder.png" # Deveria existir

    # ============================================
    # 🆕 PUBLICADOR V5.0 (SEO INJECTION)
    # ============================================
    def publish_to_wordpress(self, content: Dict, article_hash: str, original: ArticleData, image_path: str = None) -> bool:
        # Configuração Manual vs Automática
        require_approval = self._get_setting('require_manual_approval', 'true').lower() == 'true'
        
        # 1. Enriquecimento de Conteúdo
        youtube_url = self.fetch_youtube_video(content['titulo'], content.get('palavras_chave', []))
        
        enhanced_html = content['conteudo_completo']
        if youtube_url:
            enhanced_html += f'\n\n<h3>📺 Assista:</h3><p><a href="{youtube_url}" target="_blank">Ver vídeo relacionado</a></p>'
        enhanced_html += f'\n<hr><p><small>Fonte: <a href="{original.url}">{original.source}</a></small></p>'

        # 2. Fluxo de Aprovação
        if require_approval:
            save_for_approval({
                **content, 
                'conteudo_completo': enhanced_html,
                'source_url': original.url, 
                'source_name': original.source,
                'youtube_url': youtube_url,
                'image_path': image_path
            })
            # Salva no banco como pendente (log apenas)
            self._save_db(article_hash, original.url, content['titulo'], enhanced_html, original.source, content.get('qualidade_score', 0), "PENDING")
            return True

        # 3. Publicação Direta (API)
        wp_url = self._get_setting('wordpress_url')
        wp_user = self._get_setting('wordpress_username')
        wp_pass = self._get_setting('wordpress_password')
        
        if not all([wp_url, wp_user, wp_pass]): return False

        try:
            media_id = self.upload_image_to_wordpress(image_path) if image_path else None
            cat_id = self.category_map.get(content.get('categoria', 'Notícias'), 1)
            
            tags = []
            if 'palavras_chave' in content:
                for k in content['palavras_chave']:
                    if k in self.tag_map: tags.append(self.tag_map[k])

            # 🚨 SEO DEEP-LEVEL PAYLOAD 🚨
            meta_payload = {
                'youtube_url': youtube_url or '',
                'source_url': original.url,
                
                # Suporte Nativo a RankMath
                'rank_math_description': content['meta_description'],
                'rank_math_focus_keyword': content.get('palavras_chave', [''])[0],
                
                # Suporte Nativo a Yoast SEO
                '_yoast_wpseo_metadesc': content['meta_description'],
                '_yoast_wpseo_focuskw': content.get('palavras_chave', [''])[0]
            }

            post_data = {
                'title': content['titulo'],
                'content': enhanced_html,
                'excerpt': content['meta_description'], # Fallback
                'status': 'publish',
                'categories': [cat_id],
                'tags': tags,
                'featured_media': media_id,
                'meta': meta_payload 
            }
            
            # Remove chaves None/Vazias
            if not media_id: del post_data['featured_media']
            if not tags: del post_data['tags']

            r = requests.post(f'{wp_url}/wp-json/wp/v2/posts', auth=(wp_user, wp_pass), json=post_data, timeout=30)
            
            if r.status_code in [200, 201]:
                link = r.json().get('link')
                logger.info(f"✅ PUBLICADO: {link}")
                self._save_db(article_hash, original.url, content['titulo'], enhanced_html, original.source, content.get('qualidade_score', 0), link)
                return True
            else:
                logger.error(f"❌ Erro WP {r.status_code}: {r.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro publicação: {e}")
            return False

    def _save_db(self, h, url, tit, cont, src, score, wp_url):
        try:
            self.session.add(PublishedArticle(hash=h, url=url, title=tit, content_snippet=cont[:500], full_content=cont, source=src, quality_score=score, wordpress_url=wp_url, content_hash=hashlib.md5(cont.encode()).hexdigest()))
            self.session.commit()
        except: self.session.rollback()

    # ============================================
    # 🆕 CICLO DE EXECUÇÃO (TRAVA DE SEGURANÇA)
    # ============================================
    def run_cycle(self):
        logger.info(f"\n{'='*40}\n🚀 CICLO V5.0 INICIADO\n{'='*40}")
        
        # Configs de Segurança
        try:
            MAX_LIMIT = int(self._get_setting('max_articles_cycle', '5'))
        except: MAX_LIMIT = 5
        
        GENERATE_IMG = self._get_setting('generate_images', 'true').lower() == 'true'
        
        processed_count = 0
        articles = self.fetch_rss_feeds()
        
        if not articles: 
            logger.info("💤 Sem novos artigos.")
            return

        for i, article in enumerate(articles, 1):
            # 🚨 HARD LIMIT CHECK
            if processed_count >= MAX_LIMIT:
                logger.warning(f"🛑 LIMITE DE SEGURANÇA ATINGIDO ({MAX_LIMIT}). Encerrando ciclo.")
                break
                
            logger.info(f"Processando {i}/{len(articles)}: {article.title[:30]}...")
            
            full_article = self.extract_article_content(article)
            if not full_article: continue
            
            ai_content = self.process_with_gemini(full_article)
            if not ai_content: continue
            
            img_path = None
            if GENERATE_IMG:
                img_path = self.generate_image_stable_diffusion(ai_content['titulo'])
            
            success = self.publish_to_wordpress(ai_content, article.hash, article, img_path)
            
            if success:
                processed_count += 1
                time.sleep(5) # Delay anti-spam entre posts

        logger.info("✅ Ciclo finalizado.")

def main():
    # Configuração estática mínima (Feed URLs podem ser movidos para o banco no futuro)
    static_conf = {
        'rss_feeds': [
            'https://techcrunch.com/feed/',
            'https://canaltech.com.br/rss/',
            'https://g1.globo.com/rss/g1/tecnologia/'
        ]
    }
    
    robot = ContentRobot(static_conf)
    
    # Executa primeiro ciclo imediatamente
    robot.run_cycle()
    
    # Agendamento
    interval = int(robot._get_setting('check_interval_minutes', '120'))
    schedule.every(interval).minutes.do(robot.run_cycle)
    
    # Limpeza de cache diária
    schedule.every().day.at("03:30").do(lambda: robot.cache_manager.clean_expired_cache())
    
    logger.info(f"🕰️ Agendado para rodar a cada {interval} minutos.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()