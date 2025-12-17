"""Minimal smoke tests to keep CI green and validate core bootstrap paths."""
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Garantir que o pacote src seja importável no runner do CI
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import src.config.database as database


def test_init_db_uses_temp_sqlite(tmp_path, monkeypatch):
    """Ensure init_db can create schema against an isolated sqlite file."""
    db_path = tmp_path / "content_robot_test.db"

    monkeypatch.setattr(database, "DB_PATH", str(db_path))
    monkeypatch.setattr(database, "DATABASE_URL", f"sqlite:///{db_path}")

    engine = create_engine(database.DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(database, "engine", engine, raising=False)
    monkeypatch.setattr(database, "SessionLocal", SessionLocal, raising=False)

    database.Base.metadata.bind = engine
    database.init_db()

    assert os.path.exists(db_path)


def test_dashboard_importable():
    """Importing the dashboard should not raise (routes are defined)."""
    from src.interface.dashboard_app import app

    assert app is not None
