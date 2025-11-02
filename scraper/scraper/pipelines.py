import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PostgresPipeline:
    """
    Pipeline to store scraped items in PostgreSQL
    """

    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_config=crawler.settings.get('DATABASE_CONFIG')
        )

    def open_spider(self, spider):
        """
        Initialize database connection when spider opens
        """
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("Database connection established")
            
            # Create table if not exists
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, link)
                )
            """)
            self.connection.commit()
            logger.info("Quotes table ready")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def close_spider(self, spider):
        """
        Close database connection when spider closes
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Database connection closed")

    def process_item(self, item, spider):
        """
        Process and store each scraped item
        """
        try:
            self.cursor.execute("""
                INSERT INTO quotes (title, link, scraped_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (title, link) DO NOTHING
            """, (
                item.get('title'),
                item.get('link'),
                item.get('scraped_at', datetime.utcnow())
            ))
            self.connection.commit()
            logger.info(f"Stored item: {item.get('title')}")
            
        except Exception as e:
            logger.error(f"Error storing item: {e}")
            self.connection.rollback()
            
        return item