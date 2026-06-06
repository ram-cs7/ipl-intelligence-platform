from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.models import Base

import os, shutil
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SOURCE_DB = os.path.join(BASE_DIR, "ipl.db")

# On Streamlit Cloud the source dir can be read-only; SQLite needs write
# access for journal files even on SELECT queries.  Copy to /tmp if needed.
if os.path.exists(_SOURCE_DB) and not os.access(os.path.dirname(_SOURCE_DB), os.W_OK):
    DB_PATH = os.path.join("/tmp", "ipl.db")
    if not os.path.exists(DB_PATH):
        shutil.copy2(_SOURCE_DB, DB_PATH)
else:
    DB_PATH = _SOURCE_DB

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
