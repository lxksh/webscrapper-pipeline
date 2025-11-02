from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from api.tasks import run_spider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Web Scraper API",
    description="API to trigger web scraping tasks and retrieve scraped data",
    version="1.0.0"
)


class SpiderRequest(BaseModel):
    """Request model for triggering spider"""
    spider_name: str = "example_spider"


class SpiderResponse(BaseModel):
    """Response model for spider trigger"""
    task_id: str
    status: str
    message: str


def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            database=os.getenv('POSTGRES_DB', 'scraperdb'),
            user=os.getenv('POSTGRES_USER', 'scraperuser'),
            password=os.getenv('POSTGRES_PASSWORD', 'scraperpass123')
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Web Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "trigger_spider": "/api/scrape",
            "get_quotes": "/api/quotes",
            "task_status": "/api/task/{task_id}",
            "health": "/health"
        }
    }


@app.post("/api/scrape", response_model=SpiderResponse)
async def trigger_spider(request: SpiderRequest):
    """
    Trigger a spider to start scraping
    
    Args:
        request: SpiderRequest with spider_name
        
    Returns:
        SpiderResponse with task_id and status
    """
    try:
        logger.info(f"Triggering spider: {request.spider_name}")
        
        # Trigger Celery task
        task = run_spider.delay(request.spider_name)
        
        return SpiderResponse(
            task_id=task.id,
            status="queued",
            message=f"Spider {request.spider_name} queued for execution"
        )
        
    except Exception as e:
        logger.error(f"Error triggering spider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a scraping task
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status information
    """
    try:
        from celery.result import AsyncResult
        
        task = AsyncResult(task_id, app=run_spider.app)
        
        response = {
            "task_id": task_id,
            "status": task.state,
            "result": task.result if task.ready() else None
        }
        
        if task.state == 'PROGRESS':
            response['meta'] = task.info
            
        return response
        
    except Exception as e:
        logger.error(f"Error fetching task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quotes")
async def get_quotes(
    limit: int = 50,
    offset: int = 0
):
    """
    Retrieve scraped quotes from database
    
    Args:
        limit: Number of quotes to return (default: 50)
        offset: Offset for pagination (default: 0)
        
    Returns:
        List of scraped quotes
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM quotes")
        total = cursor.fetchone()['total']
        
        # Get quotes with pagination
        cursor.execute("""
            SELECT id, title, link, scraped_at
            FROM quotes
            ORDER BY scraped_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        quotes = cursor.fetchall()
        
        cursor.close()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "quotes": quotes
        }
        
    except Exception as e:
        logger.error(f"Error fetching quotes: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if conn:
            conn.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', 8000))
    )