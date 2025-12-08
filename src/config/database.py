import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "content_robot.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    return SessionLocal()

def init_db():
    try:
        from src.models import schema
        Base.metadata.create_all(bind=engine)
        print(f"✅ Banco de dados inicializado: {DB_PATH}")
    except Exception as e:
        print(f"❌ Erro ao inicializar DB: {e}")