import psycopg2
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready"""
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'postgres'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'scraperdb'),
        'user': os.getenv('POSTGRES_USER', 'scraperuser'),
        'password': os.getenv('POSTGRES_PASSWORD', 'scraperpass123')
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})")
            conn = psycopg2.connect(**db_config)
            conn.close()
            logger.info("Database is ready!")
            return True
        except psycopg2.OperationalError as e:
            logger.warning(f"Database not ready: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                logger.error("Max retries reached. Database is not available.")
                return False
    
    return False


def init_database():
    """Initialize database schema"""
    if not wait_for_db():
        raise Exception("Database initialization failed")
    
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'postgres'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'scraperdb'),
        'user': os.getenv('POSTGRES_USER', 'scraperuser'),
        'password': os.getenv('POSTGRES_PASSWORD', 'scraperpass123')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Create quotes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(title, link)
            )
        """)
        
        # Create index on scraped_at for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_quotes_scraped_at 
            ON quotes(scraped_at DESC)
        """)
        
        conn.commit()
        logger.info("Database schema initialized successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    init_database()