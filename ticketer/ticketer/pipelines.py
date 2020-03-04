# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

from .items import TransportInfo


class TicketerPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonCrawlerPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item: TransportInfo, spider):
        line = json.dumps(item.to_dict()) + '\n'
        self.file.write(line)

        return item


class SeatsFoundPipeline(object):

    def process_item(self, item: TransportInfo, spider):
        print('Your seats were found!')

        print(f'Transport ID {item["id"]}')
        print(f'Leaves {item["expedites"]}')
        print(f'Arrives {item["arrives"]}')
        for seat in item.requested_seats:
            print(f'Seats: {seat["remaining"]} remaining at {seat["price"]} price')

        print()
        return item
