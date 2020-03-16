# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from typing import List

import scrapy


class SeatInfo(scrapy.Item):
    type = scrapy.Field()
    price = scrapy.Field()
    remaining = scrapy.Field()

    def to_dict(self) -> dict:
        return dict(self)


class TransportInfo(scrapy.Item):
    id = scrapy.Field()
    direction = scrapy.Field()
    expedites = scrapy.Field()
    arrives = scrapy.Field()
    duration = scrapy.Field()
    seats = scrapy.Field()
    requested_type = scrapy.Field()

    @property
    def requested_seats(self) -> List[SeatInfo]:
        if self['requested_type']:
            return [seat for seat in self['seats'] if seat['type'] == self['requested_type']]
        else:
            return self['seats']

    def to_dict(self) -> dict:
        dumped = dict(self)
        dumped['seats'] = [seat.to_dict() for seat in self['seats']]

        return dumped
