Write-Host "Testing Web Scraper System..." -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing health endpoint..." -ForegroundColor Yellow
$health = curl.exe http://localhost/health
Write-Host $health -ForegroundColor Cyan
Write-Host ""

# Test 2: Root endpoint
Write-Host "2. Testing root endpoint..." -ForegroundColor Yellow
$root = curl.exe http://localhost/
Write-Host $root -ForegroundColor Cyan
Write-Host ""

# Test 3: Trigger scrape
Write-Host "3. Triggering spider..." -ForegroundColor Yellow
$scrape = curl.exe -X POST http://localhost/api/scrape -H "Content-Type: application/json" -d '{\"spider_name\":\"example_spider\"}'
Write-Host $scrape -ForegroundColor Cyan
Write-Host ""

Write-Host "Waiting 30 seconds for scraping to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test 4: Get quotes
Write-Host "4. Fetching quotes..." -ForegroundColor Yellow
$quotes = curl.exe "http://localhost/api/quotes?limit=5"
Write-Host $quotes -ForegroundColor Cyan
Write-Host ""

Write-Host "Testing complete! Open http://localhost/docs for interactive API documentation" -ForegroundColor Green