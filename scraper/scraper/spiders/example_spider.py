import scrapy
from scraper.items import QuoteItem
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExampleSpider(scrapy.Spider):
    """
    Spider to scrape quotes from quotes.toscrape.com
    """
    name = 'example_spider'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['https://quotes.toscrape.com/']

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 4,
    }

    def parse(self, response):
        """
        Parse the main page and extract quotes
        """
        logger.info(f"Parsing: {response.url}")
        
        # Extract all quote containers
        quotes = response.css('div.quote')
        
        for quote in quotes:
            item = QuoteItem()
            
            # Extract title (quote text)
            title = quote.css('span.text::text').get()
            
            # Extract author link
            author_link = quote.css('a[href*="/author/"]::attr(href)').get()
            
            if title and author_link:
                item['title'] = title.strip()
                item['link'] = response.urljoin(author_link)
                item['scraped_at'] = datetime.utcnow()
                
                yield item
        
        # Follow pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, callback=self.parse)
        else:
            logger.info("No more pages to scrape")