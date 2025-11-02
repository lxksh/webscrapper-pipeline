# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class QuoteItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    scraped_at = scrapy.Field()
