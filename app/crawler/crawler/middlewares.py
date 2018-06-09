# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from settings import MOCKED_DATA_PATH


class CrawlerSpiderMiddleware(object):
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

        # Should return either None or an iterable of Response, dict
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


class MockedSpiderMiddleware(object):

    def process_spider_output(self, response, result, spider):
        with open(MOCKED_DATA_PATH, 'w') as fout:
            fout.write(response.body)
        for i in result:
            yield i


class TrainScheduleSpiderMiddleware(object):

    def process_spider_output(self, response, result, spider):
        min_places = int(spider.settings['MIN_PLACES'])
        train_num = spider.settings['TRAIN_NUM']
        place_type = spider.settings['PLACE_TYPE']
        found = False

        for train in result:
            if train_num is None or train_num == train['id']:
                places = train['places']
                if place_type:
                    places = filter(lambda pl: pl.type == place_type, train['places'])
                for place in places:

                    def is_available(place):
                        return True

                    if is_available(place):
                        found = True
                        print '~~~~~~~~~~~~~~~~~~~~AVAILABLE~~~~~~~~~~~~~~~~~~~~'
                        print unicode(train)
            yield train


class MockedDownloaderMiddleware(object):

    def process_request(self, request, spider):
        from scrapy.http import HtmlResponse
        with open(MOCKED_DATA_PATH, 'r') as fin:
            body = fin.read()
        response = HtmlResponse(url=request.url,
            body=body)
        return response
