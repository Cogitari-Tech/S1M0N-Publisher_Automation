"""
Sistema de Cache Inteligente para Content Robot v4.0
Previne excesso de chamadas às APIs de IA e otimiza performance
"""
import hashlib
import json
import pickle
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
Base = declarative_base()

# ============================================
# MODELO DE CACHE
# ============================================
class CachedContent(Base):
    """Cache de conteúdo gerado por IA"""
    __tablename__ = 'cached_content'
    
    id = Column(Integer, primary_key=True)
    content_hash = Column(String(64), unique=True, index=True)
    input_title = Column(String(500))
    input_content_snippet = Column(Text)
    
    # Resultado cacheado
    cached_result = Column(Text)  # JSON do resultado
    ai_provider = Column(String(50))
    prompt_id = Column(String(100))
    
    # Metadados
    hit_count = Column(Integer, default=0)
    last_hit = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    is_valid = Column(Boolean, default=True)

class YouTubeCache(Base):
    """Cache de buscas do YouTube"""
    __tablename__ = 'youtube_cache'
    
    id = Column(Integer, primary_key=True)
    query_hash = Column(String(64), unique=True, index=True)
    query_text = Column(String(500))
    video_url = Column(String(500))
    video_title = Column(String(500))
    
    hit_count = Column(Integer, default=0)
    last_hit = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)

class ImageCache(Base):
    """Cache de imagens geradas"""
    __tablename__ = 'image_cache'
    
    id = Column(Integer, primary_key=True)
    prompt_hash = Column(String(64), unique=True, index=True)
    prompt_text = Column(String(1000))
    image_path = Column(String(500))
    
    hit_count = Column(Integer, default=0)
    last_hit = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)

# ============================================
# GERENCIADOR DE CACHE
# ============================================
class CacheManager:
    """Gerenciador central de cache"""
    
    def __init__(self, cache_dir: str = 'cache', ttl_days: int = 7):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_days = ttl_days
        
        # Configurar banco
        engine = create_engine('sqlite:///content_robot.db', echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        
        logger.info(f"✅ Cache Manager inicializado (TTL: {ttl_days} dias)")
    
    def _generate_hash(self, *args) -> str:
        """Gera hash único para cache key"""
        content = '|'.join(str(arg) for arg in args)
        return hashlib.sha256(content.encode()).hexdigest()
    
    # ==========================================
    # CACHE DE CONTEÚDO GERADO POR IA
    # ==========================================
    def get_cached_content(self, title: str, content: str, ai_provider: str) -> Optional[Dict]:
        """Busca conteúdo no cache"""
        try:
            content_hash = self._generate_hash(title, content[:1000], ai_provider)
            
            cached = self.session.query(CachedContent).filter_by(
                content_hash=content_hash,
                is_valid=True
            ).first()
            
            if cached:
                # Verifica expiração
                if cached.expires_at and datetime.now() > cached.expires_at:
                    logger.info("⏰ Cache expirado")
                    return None
                
                # Atualiza estatísticas
                cached.hit_count += 1
                cached.last_hit = datetime.now()
                self.session.commit()
                
                result = json.loads(cached.cached_result)
                logger.info(f"✅ Cache HIT! (usado {cached.hit_count}x)")
                return result
            
            logger.info("❌ Cache MISS")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar cache: {e}")
            return None
    
    def save_cached_content(self, title: str, content: str, ai_provider: str, 
                           result: Dict, prompt_id: str = 'default'):
        """Salva conteúdo no cache"""
        try:
            content_hash = self._generate_hash(title, content[:1000], ai_provider)
            
            cached = CachedContent(
                content_hash=content_hash,
                input_title=title,
                input_content_snippet=content[:500],
                cached_result=json.dumps(result, ensure_ascii=False),
                ai_provider=ai_provider,
                prompt_id=prompt_id,
                expires_at=datetime.now() + timedelta(days=self.ttl_days)
            )
            
            self.session.add(cached)
            self.session.commit()
            
            logger.info(f"💾 Conteúdo cacheado (expira em {self.ttl_days} dias)")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erro ao salvar cache: {e}")
    
    # ==========================================
    # CACHE DE YOUTUBE
    # ==========================================
    def get_cached_youtube(self, title: str, keywords: list) -> Optional[str]:
        """Busca vídeo do YouTube no cache"""
        try:
            query = f"{title} {' '.join(keywords[:3])}"
            query_hash = self._generate_hash(query)
            
            cached = self.session.query(YouTubeCache).filter_by(
                query_hash=query_hash
            ).first()
            
            if cached:
                # Verifica expiração (YouTube muda menos)
                if cached.expires_at and datetime.now() > cached.expires_at:
                    return None
                
                cached.hit_count += 1
                cached.last_hit = datetime.now()
                self.session.commit()
                
                logger.info(f"✅ YouTube Cache HIT: {cached.video_url}")
                return cached.video_url
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar cache YouTube: {e}")
            return None
    
    def save_cached_youtube(self, title: str, keywords: list, video_url: str, video_title: str = ''):
        """Salva vídeo do YouTube no cache"""
        try:
            query = f"{title} {' '.join(keywords[:3])}"
            query_hash = self._generate_hash(query)
            
            cached = YouTubeCache(
                query_hash=query_hash,
                query_text=query,
                video_url=video_url,
                video_title=video_title,
                expires_at=datetime.now() + timedelta(days=30)  # 30 dias para YouTube
            )
            
            self.session.add(cached)
            self.session.commit()
            
            logger.info(f"💾 YouTube cacheado: {video_url}")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erro ao salvar cache YouTube: {e}")
    
    # ==========================================
    # CACHE DE IMAGENS
    # ==========================================
    def get_cached_image(self, prompt: str) -> Optional[str]:
        """Busca imagem no cache"""
        try:
            prompt_hash = self._generate_hash(prompt)
            
            cached = self.session.query(ImageCache).filter_by(
                prompt_hash=prompt_hash
            ).first()
            
            if cached:
                # Verifica se arquivo existe
                if not os.path.exists(cached.image_path):
                    logger.warning("⚠️ Imagem cacheada não encontrada no disco")
                    return None
                
                # Verifica expiração
                if cached.expires_at and datetime.now() > cached.expires_at:
                    return None
                
                cached.hit_count += 1
                cached.last_hit = datetime.now()
                self.session.commit()
                
                logger.info(f"✅ Image Cache HIT: {cached.image_path}")
                return cached.image_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar cache de imagem: {e}")
            return None
    
    def save_cached_image(self, prompt: str, image_path: str):
        """Salva imagem no cache"""
        try:
            prompt_hash = self._generate_hash(prompt)
            
            cached = ImageCache(
                prompt_hash=prompt_hash,
                prompt_text=prompt[:1000],
                image_path=image_path,
                expires_at=datetime.now() + timedelta(days=90)  # 90 dias para imagens
            )
            
            self.session.add(cached)
            self.session.commit()
            
            logger.info(f"💾 Imagem cacheada: {image_path}")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erro ao salvar cache de imagem: {e}")
    
    # ==========================================
    # ESTATÍSTICAS E LIMPEZA
    # ==========================================
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        try:
            content_count = self.session.query(CachedContent).count()
            youtube_count = self.session.query(YouTubeCache).count()
            image_count = self.session.query(ImageCache).count()
            
            content_hits = self.session.query(CachedContent).filter(
                CachedContent.hit_count > 0
            ).count()
            
            total_cache_size = 0
            if self.cache_dir.exists():
                for file in self.cache_dir.rglob('*'):
                    if file.is_file():
                        total_cache_size += file.stat().st_size
            
            # Tamanho das imagens
            image_size = 0
            images = self.session.query(ImageCache).all()
            for img in images:
                if os.path.exists(img.image_path):
                    image_size += os.path.getsize(img.image_path)
            
            return {
                'content_cached': content_count,
                'youtube_cached': youtube_count,
                'images_cached': image_count,
                'content_hit_rate': round((content_hits / content_count * 100) if content_count > 0 else 0, 1),
                'cache_size_mb': round((total_cache_size + image_size) / 1024 / 1024, 2),
                'storage_saved_calls': content_hits + youtube_count + image_count
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter stats: {e}")
            return {}
    
    def clean_expired_cache(self) -> Dict[str, int]:
        """Remove cache expirado"""
        try:
            deleted = {'content': 0, 'youtube': 0, 'images': 0}
            
            # Limpa conteúdo expirado
            expired_content = self.session.query(CachedContent).filter(
                CachedContent.expires_at < datetime.now()
            ).all()
            
            for item in expired_content:
                self.session.delete(item)
                deleted['content'] += 1
            
            # Limpa YouTube expirado
            expired_youtube = self.session.query(YouTubeCache).filter(
                YouTubeCache.expires_at < datetime.now()
            ).all()
            
            for item in expired_youtube:
                self.session.delete(item)
                deleted['youtube'] += 1
            
            # Limpa imagens expiradas
            expired_images = self.session.query(ImageCache).filter(
                ImageCache.expires_at < datetime.now()
            ).all()
            
            for item in expired_images:
                # Remove arquivo do disco
                if os.path.exists(item.image_path):
                    try:
                        os.remove(item.image_path)
                    except:
                        pass
                
                self.session.delete(item)
                deleted['images'] += 1
            
            self.session.commit()
            
            logger.info(f"🧹 Cache limpo: {sum(deleted.values())} itens removidos")
            return deleted
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erro ao limpar cache: {e}")
            return {'content': 0, 'youtube': 0, 'images': 0}
    
    def clear_all_cache(self) -> bool:
        """Remove TODO o cache (use com cuidado!)"""
        try:
            # Remove do banco
            self.session.query(CachedContent).delete()
            self.session.query(YouTubeCache).delete()
            
            # Remove imagens do disco
            images = self.session.query(ImageCache).all()
            for img in images:
                if os.path.exists(img.image_path):
                    try:
                        os.remove(img.image_path)
                    except:
                        pass
            
            self.session.query(ImageCache).delete()
            self.session.commit()
            
            logger.warning("🗑️ TODO o cache foi removido!")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erro ao limpar cache: {e}")
            return False
    
    def invalidate_content_cache(self, content_hash: str):
        """Invalida um item específico do cache"""
        try:
            cached = self.session.query(CachedContent).filter_by(
                content_hash=content_hash
            ).first()
            
            if cached:
                cached.is_valid = False
                self.session.commit()
                logger.info(f"❌ Cache invalidado: {content_hash[:8]}")
                
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erro ao invalidar cache: {e}")


# ==========================================
# TESTES
# ==========================================
if __name__ == '__main__':
    print("🧪 Testando Cache Manager...\n")
    
    cache = CacheManager(ttl_days=7)
    
    # Teste 1: Cache de conteúdo
    print("1️⃣ Testando cache de conteúdo...")
    test_result = {'titulo': 'Teste', 'conteudo': 'Lorem ipsum'}
    cache.save_cached_content('Título Teste', 'Conteúdo teste', 'gemini', test_result)
    cached = cache.get_cached_content('Título Teste', 'Conteúdo teste', 'gemini')
    print(f"   Resultado: {'✅ OK' if cached else '❌ FALHOU'}\n")
    
    # Teste 2: Cache YouTube
    print("2️⃣ Testando cache YouTube...")
    cache.save_cached_youtube('AI News', ['artificial', 'intelligence'], 
                              'https://youtube.com/watch?v=test', 'Video Test')
    cached_yt = cache.get_cached_youtube('AI News', ['artificial', 'intelligence'])
    print(f"   Resultado: {'✅ OK' if cached_yt else '❌ FALHOU'}\n")
    
    # Teste 3: Estatísticas
    print("3️⃣ Estatísticas do cache:")
    stats = cache.get_cache_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Testes concluídos!")