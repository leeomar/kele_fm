#/bin/python
from scrapy.xlib.pydispatch import dispatcher
from scrapy.exceptions import DontCloseSpider
from scrapy import signals
from scrapy import log

class SeedAppend(object):

    def __init__(self):
        dispatcher.connect(self.spider_idle, signal=signals.spider_idle)

    def spider_idle(self):
        
        return DontCloseSpider
