from scrapy import signals
from scrapy.http import HtmlResponse
import logging

logger = logging.getLogger(__name__)


class ScraperSpiderMiddleware:
    """
    Spider middleware for custom processing
    """

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        logger.error(f"Spider exception: {exception}")
        pass

    def spider_opened(self, spider):
        logger.info(f'Spider opened: {spider.name}')


class ScraperDownloaderMiddleware:
    """
    Downloader middleware for request/response processing
    """

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        logger.error(f"Download exception: {exception}")
        pass

    def spider_opened(self, spider):
        logger.info(f'Spider opened: {spider.name}')