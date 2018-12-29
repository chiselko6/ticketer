# -*- coding: utf-8 -*-
import json
import copy
from items import TransportInfo

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class JsonCrawlerPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        processed_item = dict(item)
        if isinstance(item, TransportInfo):
            processed_item['seats'] = map(dict, item['seats'])
        line = json.dumps(processed_item) + '\n'
        self.file.write(line)
        return processed_item


class TransportFoundPipeline(object):

    def process_item(self, item, spider):
        print 'Your train was found!'
        print repr(item)
        return item
