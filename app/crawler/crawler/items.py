# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TrainSeat(scrapy.Item):
    type = scrapy.Field()
    price = scrapy.Field()
    remaining = scrapy.Field()

    def __repr__(self):
        return 'Remaining: {}, price: {}'.format(self['remaining'], self['price'])

    def __str__(self):
        return u'{} {} {}'.format(self['type'], self['price'], self['remaining'])


class TrainInfo(scrapy.Item):
    id = scrapy.Field()
    direction = scrapy.Field()
    expedites = scrapy.Field()
    arrives = scrapy.Field()
    duration = scrapy.Field()
    seats = scrapy.Field()
    requested_type = scrapy.Field()

    @property
    def requested_seat(self):
        if self['requested_type']:
            return filter(lambda s: s['type'] == self['requested_type'], self['seats'])[0]
        return None

    def __repr__(self):
        requested_seat = self.requested_seat or self['seats']
        return u'Train #{}\nDeparture: {}\nArrival: {}\nAvailable seats: {}\n'.format(
            self['id'],
            self['expedites'],
            self['arrives'],
            repr(requested_seat),
        )

    def __str__(self):
        return u'Train #{} {}: {}-{}({})\nAvailable: {}'.format(
            self['id'], self['direction'], self['expedites'], self['arrives'],
            self['duration'],
            ','.join(map(lambda s: u'({})'.format(s), self['seats'])))
