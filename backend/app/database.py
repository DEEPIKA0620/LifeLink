import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger("lifelink")

db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///./"):
    from pathlib import Path
    backend_dir = Path(__file__).resolve().parent.parent
    db_file = db_url.replace("sqlite:///./", "")
    db_path = (backend_dir / db_file).resolve().as_posix()
    db_url = f"sqlite:///{db_path}"
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and "+psycopg2" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True
    )
    # Test connection
    with engine.connect() as conn:
        logger.info(f"Connected to database successfully ({db_url.split('@')[-1] if '@' in db_url else db_url})")
except Exception as e:
    logger.warning(f"Failed to connect to primary database ({db_url}): {e}. Falling back to SQLite.")
    fallback_url = "sqlite:///./lifelink.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
