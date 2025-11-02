from celery import Celery
import subprocess
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'scraper_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, name='api.tasks.run_spider')
def run_spider(self, spider_name):
    """
    Celery task to run a Scrapy spider using subprocess
    
    Args:
        spider_name: Name of the spider to run
        
    Returns:
        dict: Task result with status and stats
    """
    try:
        logger.info(f"Starting spider: {spider_name}")
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'status': 'Starting spider...'})
        
        # Run scrapy spider using subprocess
        result = subprocess.run(
            ['scrapy', 'crawl', spider_name],
            cwd='/scraper',
            capture_output=True,
            text=True,
            timeout=3600,
            env={**os.environ, 'PYTHONPATH': '/scraper'}
        )
        
        if result.returncode == 0:
            logger.info(f"Spider {spider_name} completed successfully")
            return {
                'status': 'completed',
                'spider': spider_name,
                'message': f'Spider {spider_name} finished scraping',
                'stdout': result.stdout[-500:] if result.stdout else ''  # Last 500 chars
            }
        else:
            logger.error(f"Spider {spider_name} failed with return code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            return {
                'status': 'failed',
                'spider': spider_name,
                'error': result.stderr[-500:] if result.stderr else 'Unknown error',
                'return_code': result.returncode
            }
        
    except subprocess.TimeoutExpired:
        logger.error(f"Spider {spider_name} timed out")
        return {
            'status': 'failed',
            'spider': spider_name,
            'error': 'Spider execution timed out after 1 hour'
        }
    except Exception as e:
        logger.error(f"Error running spider {spider_name}: {str(e)}")
        return {
            'status': 'failed',
            'spider': spider_name,
            'error': str(e)
        }