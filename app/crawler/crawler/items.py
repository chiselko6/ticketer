# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TrainPlace(scrapy.Item):
    type = scrapy.Field()
    price = scrapy.Field()
    remaining = scrapy.Field()


class TrainInfo(scrapy.Item):
    id = scrapy.Field()
    direction = scrapy.Field()
    start = scrapy.Field()
    end = scrapy.Field()
    duration = scrapy.Field()
    places = scrapy.Field()
