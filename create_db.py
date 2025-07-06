import logging
from app.db.database import init_db, SQLALCHEMY_DATABASE_URL
import os

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    logger.info(f"Attempting to initialize database at: {SQLALCHEMY_DATABASE_URL}")
    init_db()
    logger.info("Database initialized successfully.")
