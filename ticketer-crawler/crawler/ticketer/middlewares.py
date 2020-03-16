# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from typing import Iterable, Optional

from scrapy import signals
import requests

from .items import TransportInfo, SeatInfo
from .settings import MOCKED_DATA_PATH


class TicketerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TicketerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MockedSpiderMiddleware(object):

    def process_spider_output(self, response, result: Iterable[TransportInfo], spider):
        with open(MOCKED_DATA_PATH, 'w') as fout:
            fout.write(response.body)
        for i in result:
            yield i


class TransportScheduleSpiderMiddleware(object):

    def __init__(self, min_seats: int = 1, num: Optional[str] = None, seat_type: Optional[str] = None) -> None:
        self.min_seats = min_seats
        self.num = num
        self.seat_type = seat_type

    @classmethod
    def from_crawler(cls, crawler):
        min_seats = crawler.settings['MIN_SEATS']
        return cls(
            min_seats=int(min_seats) if min_seats is not None else 1,
            num=crawler.settings['NUM'],
            seat_type=crawler.settings['SEAT_TYPE'],
        )

    def process_spider_output(self, response, result: Iterable[TransportInfo], spider):

        def eligible_transport(transport: TransportInfo) -> bool:
            return self.num is None or self.num == transport['id']

        def eligible_seat(seat: SeatInfo) -> bool:
            return self.seat_type is None or seat['type'] == self.seat_type

        def eligible_seats(seats: Iterable[SeatInfo]) -> Iterable[SeatInfo]:
            return filter(eligible_seat, seats)

        def available_seat(seat: SeatInfo) -> bool:
            remaining = seat['remaining']
            if remaining is None:
                return False

            return int(remaining) >= self.min_seats

        found_any = False

        for transport in result:
            found = False

            if eligible_transport(transport):
                seats = eligible_seats(transport['seats'])
                for seat in seats:
                    if available_seat(seat):
                        found = True

            found_any = found_any or found

            if found:
                yield transport

        if not found_any:
            yield response.request


class JobScheduleSpiderMiddleware(TransportScheduleSpiderMiddleware):

    def __init__(self, retry_url: str, job_id: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.retry_url = retry_url
        self.job_id = job_id

    @classmethod
    def from_crawler(cls, crawler):
        min_seats = crawler.settings['MIN_SEATS']
        return cls(
            min_seats=int(min_seats) if min_seats is not None else 1,
            num=crawler.settings['NUM'],
            seat_type=crawler.settings['SEAT_TYPE'],
            retry_url=crawler.settings['RETRY_URL'],
            job_id=crawler.settings['JOB_ID'],
        )

    def process_spider_output(self, response, result: Iterable[TransportInfo], spider):
        was_found = False

        for item in super().process_spider_output(response, result, spider):
            if isinstance(item, TransportInfo):
                was_found = True
                yield item

        if not was_found:
            requests.post(self.retry_url, json={'job_id': self.job_id})
            yield None


class MockedDownloaderMiddleware(object):

    def process_request(self, request, spider):
        from scrapy.http import HtmlResponse

        with open(MOCKED_DATA_PATH, 'r') as fin:
            body = fin.read()
        response = HtmlResponse(url=request.url,
                                body=body)
        return response
