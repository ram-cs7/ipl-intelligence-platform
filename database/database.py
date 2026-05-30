from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.models import Base

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "ipl.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_sql(query: str, params: dict = None):
    """Execute raw SQL and return results as list of dicts — used for analytics endpoints."""
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        cols = result.keys()
        return [dict(zip(cols, row)) for row in result.fetchall()]
