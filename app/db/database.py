import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Resolve the absolute path for SQLite database
if SQLALCHEMY_DATABASE_URL.startswith(
    "sqlite:///"
) and not SQLALCHEMY_DATABASE_URL.startswith("sqlite:////"):
    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///./", "")
    absolute_db_path = os.path.abspath(db_path)
    logger.debug(f"Resolved SQLite DB path: {absolute_db_path}")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{absolute_db_path}"

logger.debug(f"Connecting to database at: {SQLALCHEMY_DATABASE_URL}")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    logger.debug("Attempting to create all tables...")
    Base.metadata.create_all(bind=engine)
    logger.debug("Table creation attempt finished.")
