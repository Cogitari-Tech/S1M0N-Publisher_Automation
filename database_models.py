"""
Modelos de Banco de Dados - Content Robot v5.0
Arquivo central de definições de schema (SQLAlchemy)
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# ============================================
# 1. TABELA DE CONFIGURAÇÕES (NOVA v5.0)
# ============================================
class SystemSettings(Base):
    """
    Armazena configurações dinâmicas do sistema.
    Substitui a dependência do .env para dados mutáveis via Dashboard.
    """
    __tablename__ = 'system_settings'

    key = Column(String(100), primary_key=True)
    value = Column(Text)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# ============================================
# 2. TABELAS DE CONTEÚDO
# ============================================
class PublishedArticle(Base):
    __tablename__ = 'published_articles'
    
    id = Column(Integer, primary_key=True)
    hash = Column(String(32), unique=True, index=True)
    url = Column(String(500))
    title = Column(String(500))
    content_hash = Column(String(32), index=True)
    content_snippet = Column(Text)
    full_content = Column(Text)
    source = Column(String(200))
    published_date = Column(DateTime, default=datetime.now)
    quality_score = Column(Float)
    originality_score = Column(Float)
    wordpress_url = Column(String(500))

# ============================================
# 3. TABELAS DE LOGS E METRICAS
# ============================================
class RateLimitLog(Base):
    __tablename__ = 'rate_limit_logs'
    
    id = Column(Integer, primary_key=True)
    service = Column(String(50), index=True)
    last_request = Column(DateTime, default=datetime.now)

class APIUsageLog(Base):
    __tablename__ = 'api_usage_logs'
    
    id = Column(Integer, primary_key=True)
    service = Column(String(50))
    calls = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.now)

# ============================================
# 4. TABELAS DE CACHE (Integradas v4.0+)
# ============================================
class CachedContent(Base):
    """Cache de conteúdo gerado por IA"""
    __tablename__ = 'cached_content'
    
    id = Column(Integer, primary_key=True)
    content_hash = Column(String(64), unique=True, index=True)
    input_title = Column(String(500))
    input_content_snippet = Column(Text)
    cached_result = Column(Text)  # JSON do resultado
    ai_provider = Column(String(50))
    prompt_id = Column(String(100))
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
# FUNÇÃO HELPER PARA CRIAR ENGINE
# ============================================
def get_database_session():
    """Retorna sessão do banco de dados"""
    engine = create_engine('sqlite:///content_robot.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()