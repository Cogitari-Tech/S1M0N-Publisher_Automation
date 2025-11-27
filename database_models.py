"""
Modelos de Banco de Dados - Content Robot v4.0
Arquivo separado para evitar importação circular
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# ============================================
# MODELOS DO BANCO
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
# FUNÇÃO HELPER PARA CRIAR ENGINE
# ============================================
def get_database_session():
    """Retorna sessão do banco de dados"""
    engine = create_engine('sqlite:///content_robot.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()