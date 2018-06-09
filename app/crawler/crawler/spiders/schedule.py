# -*- coding: utf-8 -*-
import scrapy
from crawler.items import TrainInfo, TrainPlace


class ScheduleSpider(scrapy.Spider):
    name = 'schedule'

    def start_requests(self):
        urls = [
            'https://rasp.rw.by/ru/route/?from={}&to={}&date={}&from_exp=&from_esr=&to_exp=&to_esr='.format(self.src, self.dest, self.date),
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        def map_schedule_row(row):

            def map_place_info(info):
                fields = {
                    'type': info.css('li.train_note::text').extract_first(),
                    'price': info.css('li.train_price::text').extract_first(),
                    'remaining': info.css('li.train_place a.train_seats::text').extract_first(),
                }
                return TrainPlace(**fields)

            fields = {
                'id': row.css('td.train_info small.train_id::text').extract_first(),
                'direction': row.css('td.train_info .train_name a.train_text::text').extract_first(),
                'start': row.css('td.train_start .train_start-time::text').extract_first(),
                'end': row.css('td.train_end .train_end-time::text').extract_first(),
                'duration': row.css('td.train_time .train_time-total::text').extract_first(),
                'places': map(map_place_info, row.css('td.train_details ul.train_details-group')),
            }
            return TrainInfo(**fields)

        schedule = response.css('tbody.schedule_list')[0]
        rows = schedule.css('tr')
        for row in rows:
            yield map_schedule_row(row)
