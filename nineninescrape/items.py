# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class NineninescrapeItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = Field()
    quote = Field()
    speakers = Field()
    pass
