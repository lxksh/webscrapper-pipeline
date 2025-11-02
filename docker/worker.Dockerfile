FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scraper/scraper/ ./scraper/
COPY api/ ./api/
COPY scrapy.cfg ./scraper.cfg

# Set Python path
ENV PYTHONPATH=/app

# Run Celery worker
CMD ["celery", "-A", "api.tasks", "worker", "--loglevel=info", "--concurrency=2"]