# Scrapy settings for kele_fm project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

LOG_FILE = 'tmall.log'
BOT_NAME = 'kele_fm'
BOT_VERSION = '1.0'
SELECTORS_BACKEND = "lxml"

SPIDER_MODULES = ['kele_fm.spiders']
NEWSPIDER_MODULE = 'kele_fm.spiders'
DEFAULT_ITEM_CLASS = 'kele_fm.items.KeleFmItem'
#USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)'

DOWNLOADER_MIDDLEWARES = {
    'kele_fm.middlewares.hostpolite.HostPoliteCtrlMiddleware' : 200,
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware' : 100,
    'scrapy.contrib.downloadermiddleware.stats.DownloaderStats' : 300,
    'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware' : 500,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware' : 700,
}
