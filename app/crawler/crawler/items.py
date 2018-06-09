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

    def __str__(self):
        return u'{} {} {}'.format(self['type'], self['price'], self['remaining'])


class TrainInfo(scrapy.Item):
    id = scrapy.Field()
    direction = scrapy.Field()
    expedites = scrapy.Field()
    arrives = scrapy.Field()
    duration = scrapy.Field()
    places = scrapy.Field()

    def __str__(self):
        return u'Train #{} {}: {}-{}({})\nAvailable: {}'.format(
            self['id'], self['direction'], self['expedites'], self['arrives'],
            self['duration'],
            ','.join(map(lambda pl: '({})'.format(pl), self['places'])))
