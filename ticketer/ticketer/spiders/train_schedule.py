# -*- coding: utf-8 -*-
from typing import Iterable

import scrapy

from ticketer.items import TransportInfo, SeatInfo

SCHEDULE_URL_FORMAT = 'https://rasp.rw.by/{}/route/?from={}&to={}&date={}&from_exp=&from_esr=&to_exp=&to_esr='


class TrainScheduleSpider(scrapy.Spider):
    name = 'train_schedule'

    custom_settings = {
        'MIN_SEATS': 1,
        'NUM': None,
        'SEAT_TYPE': None,
        'LANG': 'ru',
    }

    def start_requests(self):
        urls = [
            SCHEDULE_URL_FORMAT.format(
                self.settings['LANG'],
                self.src,
                self.dest,
                self.date
            ),
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response) -> Iterable[TransportInfo]:

        def map_schedule_row(row) -> TransportInfo:

            def map_seat_info(info) -> SeatInfo:
                fields = {
                    'type': info.css('li.train_note::text').extract_first(),
                    'price': info.css('li.train_price span::text')
                    .extract_first(),
                    'remaining': info.css('li.train_place a.train_seats::text')
                    .extract_first(),
                }
                return SeatInfo(**fields)

            fields = {
                'id': row.css('td.train_info small.train_id::text')
                .extract_first(),
                'direction': row.css(
                    'td.train_info .train_name a.train_text::text'
                )
                .extract_first(),
                'expedites': row.css('td.train_start .train_start-time::text')
                .extract_first(),
                'arrives': row.css('td.train_end .train_end-time::text')
                .extract_first(),
                'duration': row.css('td.train_time .train_time-total::text')
                .extract_first(),
                'seats': [
                    map_seat_info(seat)
                    for seat in row.css('td.train_details ul.train_details-group')
                ],
                'requested_type': self.settings.get('SEAT_TYPE'),
            }
            return TransportInfo(**fields)

        schedule = response.css('tbody.schedule_list')[0]
        rows = schedule.css('tr')
        for row in rows:
            yield map_schedule_row(row)
