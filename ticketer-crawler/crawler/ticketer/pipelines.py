# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import requests
import scrapy

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


class TelegramNotificationPipeline:

    def __init__(self, tg_bot_token, tg_chat_id):
        self.tg_bot_token = tg_bot_token
        self.tg_chat_id = tg_chat_id

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            tg_bot_token=crawler.settings['TG_TOKEN'],
            tg_chat_id=crawler.settings['TG_CHAT_ID'],
        )

    def process_item(self, item: TransportInfo, spider: scrapy.Spider) -> TransportInfo:
        item_repr = f'''Transport: {item['id']}
        Leaves at {item['expedites']}
        Arrives at {item['arrives']}
        '''

        for seat in item.requested_seats:
            item_repr = f'{item_repr}\nSeats: {seat["remaining"]}({seat["type"]}) remaining at {seat["price"]}'

        url = f'https://api.telegram.org/bot{self.tg_bot_token}/sendMessage?chat_id={self.tg_chat_id}&text={item_repr}'
        requests.get(url)

        return item
