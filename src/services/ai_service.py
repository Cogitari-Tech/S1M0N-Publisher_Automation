import os
import time
import json
import logging
import google.generativeai as genai
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from datetime import datetime, timedelta
from typing import Optional, Dict

from src.config.settings import settings
from src.config.database import get_db
from src.models.schema import CachedContent, ImageCache, PublishedArticle
from src.services.ai.factory import ModelFactory

# Logger
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self._setup_gemini()
        self._setup_vertex_ai()

    def _setup_gemini(self):
        try:
            self.client = ModelFactory.create_client()
        except Exception as e:
            logger.error(f"AI Client Init Error: {e}")
            self.client = None

    def _setup_vertex_ai(self):
        pid = settings.GOOGLE_PROJECT_ID
        loc = settings.GOOGLE_LOCATION
        if pid:
            try:
                vertexai.init(project=pid, location=loc)
                self.vertex_ready = True
            except: self.vertex_ready = False
        else: self.vertex_ready = False

    def _calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calcula similaridade de Jaccard entre dois textos."""
        try:
            if not text_a or not text_b: return 0.0
            def tokenize(t): return set(t.lower().split())
            set_a = tokenize(text_a)
            set_b = tokenize(text_b)
            intersection = len(set_a.intersection(set_b))
            union = len(set_a.union(set_b))
            return intersection / union if union > 0 else 1.0
        except:
            return 0.0

    def _check_double_layer_originality(self, source_text: str, generated_text: str) -> float:
        """
        CAMADA DUPLA DE PROTEÇÃO:
        1. Verifica plágio da fonte original (RSS).
        2. Verifica auto-plágio (se o robô já escreveu algo igual recentemente).
        Retorna o score de originalidade mais baixo (pior cenário).
        """
        # Camada 1: Fonte Original
        sim_source = self._calculate_similarity(source_text, generated_text)
        originality_source = 1.0 - sim_source

        # Camada 2: Histórico Recente (Buffer de 7 dias)
        db = get_db()
        try:
            last_week = datetime.now() - timedelta(days=7)
            recent_articles = db.query(PublishedArticle.content_snippet).filter(
                PublishedArticle.published_date >= last_week
            ).order_by(PublishedArticle.published_date.desc()).limit(50).all()
            
            max_sim_history = 0.0
            for article in recent_articles:
                if article.content_snippet:
                    sim = self._calculate_similarity(article.content_snippet, generated_text)
                    if sim > max_sim_history:
                        max_sim_history = sim
            
            originality_history = 1.0 - max_sim_history
            
            # O score final é o menor entre (Original vs Fonte) e (Original vs Histórico)
            final_score = min(originality_source, originality_history)
            
            if max_sim_history > 0.5:
                logger.warning(f"⚠️ Alerta de Auto-Plágio: Texto muito similar ao histórico recente ({max_sim_history:.2f})")
            
            return final_score

        except Exception as e:
            logger.error(f"Erro na verificação de histórico: {e}")
            return originality_source # Fallback seguro
        finally:
            db.close()

    def generate_article(self, news_item, is_evergreen: bool = False) -> Optional[Dict]:
        if not self.client: return None
        
        import hashlib
        content_hash = hashlib.md5(f"{news_item.title}|{news_item.summary}".encode()).hexdigest()
        
        db = get_db()
        cached = db.query(CachedContent).filter(CachedContent.content_hash == content_hash).first()
        if cached and cached.is_valid:
            db.close()
            return json.loads(cached.cached_result)

        prompt = f"""
        Você é o S1M0N, um redator de elite.
        Tarefa: Reescrever completamente o conteúdo abaixo para um blog profissional.
        
        Fonte:
        Título: {news_item.title}
        Resumo: {news_item.summary}
        
        Regras Críticas:
        1. Originalidade Extrema: Não traduza literalmente. Mude a estrutura, use sinônimos e analogias.
        2. Tom: Técnico, Autoridade, mas acessível.
        3. Formato JSON estrito.
        
        SAÍDA JSON OBRIGATÓRIA:
        {{ 
            "titulo": "Título SEO (Max 60 chars)", 
            "meta_description": "Resumo click-worthy", 
            "conteudo_completo": "<p>...</p><h2>...</h2>", 
            "palavras_chave": ["tag1", "tag2"], 
            "categoria": "Tech/Business", 
            "qualidade_score": 90,
            "originalidade_score": 95 
        }}
        """
        
        try:
            clean_text = self.client.generate(prompt)
            clean_text = clean_text.strip().replace('```json', '').replace('```', '')
            result = json.loads(clean_text)
            
            # Verificação de Integridade (Camada Dupla)
            real_originality = self._check_double_layer_originality(news_item.summary, result.get('conteudo_completo', ''))
            
            if real_originality < 0.3:
                logger.warning(f"⚠️ Artigo rejeitado por baixa originalidade ({real_originality:.2f}).")
                result['originalidade_score'] = int(real_originality * 100)
                # Opcional: Poderíamos retornar None aqui para descartar, mas mantemos com score baixo para auditoria
            
            # Salvar Cache
            db.add(CachedContent(content_hash=content_hash, input_title=news_item.title, cached_result=clean_text, ai_provider='gemini', created_at=datetime.now()))
            db.commit()
            return result
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return None
        finally:
            db.close()

    def generate_image(self, title: str) -> Optional[str]:
        if not settings.ENABLE_GLOBAL_IMAGES or not self.vertex_ready: return None
        
        import hashlib
        phash = hashlib.md5(title.encode()).hexdigest()
        db = get_db()
        cached = db.query(ImageCache).filter(ImageCache.prompt_hash == phash).first()
        if cached and os.path.exists(cached.image_path):
            db.close()
            return cached.image_path

        try:
            model = ImageGenerationModel.from_pretrained("image-3.0-generate-001")
            full_prompt = f"{settings.IMAGE_PROMPT_STYLE}. Concept: {title}. High definition, cinematic lighting."
            
            images = model.generate_images(prompt=full_prompt, number_of_images=1)
            os.makedirs('images', exist_ok=True)
            fname = f"images/vertex_{int(time.time())}.png"
            images[0].save(location=fname, include_generation_parameters=False)
            
            db.add(ImageCache(prompt_hash=phash, image_path=fname, created_at=datetime.now()))
            db.commit()
            return fname
        except Exception as e:
            logger.error(f"Vertex AI Error: {e}")
            return None
        finally:
            db.close()