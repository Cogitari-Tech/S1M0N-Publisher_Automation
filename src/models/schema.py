from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from src.config.database import Base

# ==============================================================================
# CONFIGURAÇÕES E FONTES
# ==============================================================================
class SystemSettings(Base):
    __tablename__ = 'system_settings'
    key = Column(String(100), primary_key=True)
    value = Column(Text)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class RSSFeed(Base):
    __tablename__ = 'rss_feeds'
    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True, nullable=False)
    name = Column(String(200))
    # NOVO CAMPO v7.5: Tema/Categoria do Feed
    theme = Column(String(100), default="Geral")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

# ==============================================================================
# CONTEÚDO E FLUXO
# ==============================================================================
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

class PendingArticle(Base):
    __tablename__ = 'pending_articles'
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    original_url = Column(String(500))
    source_name = Column(String(200))
    content_json = Column(Text)
    image_path = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='PENDING')

# ==============================================================================
# LOGS E CACHE
# ==============================================================================
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

class CachedContent(Base):
    __tablename__ = 'cached_content'
    id = Column(Integer, primary_key=True)
    content_hash = Column(String(64), unique=True, index=True)
    input_title = Column(String(500))
    input_content_snippet = Column(Text)
    cached_result = Column(Text)
    ai_provider = Column(String(50))
    prompt_id = Column(String(100))
    hit_count = Column(Integer, default=0)
    last_hit = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    is_valid = Column(Boolean, default=True)

class YouTubeCache(Base):
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
    __tablename__ = 'image_cache'
    id = Column(Integer, primary_key=True)
    prompt_hash = Column(String(64), unique=True, index=True)
    prompt_text = Column(String(1000))
    image_path = Column(String(500))
    hit_count = Column(Integer, default=0)
    last_hit = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)