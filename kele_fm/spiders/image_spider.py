#/bin/python
#coding: utf8

from scrapy.spider import BaseSpider
from scrapy import log
from kele_fm.upyunapi.upyun import UpYun,md5

class TmallSpider(BaseSpider):
    name = 'image.spider'
    #allowd_domains = ['tmall.com']
    start_urls = [
            'http://img04.taobaocdn.com/bao/uploaded/i4/T1fAOGXoXmXXaUY7I1_042104.jpg',
            'http://img01.taobaocdn.com/bao/uploaded/i1/T1jHVRXlddXXbRbew1_041010.jpg'
            ]
    
    def __init__(self):
        self.upyun_client = UpYun('kele-img','kele-admin','omar1984')

    def parse(self, response):
        self.log('parse %s, meta: %s' % (response.url, response.request.meta),\
                level=log.DEBUG)

        try:
            self.log('process image, url:%s' % response.url,
                    level=log.DEBUG)
            #print response.body
            print response.headers
            #image_key=response.request.meta.get('image_key')
            image_key='/tmall.jpg'
            #data = open('tmp.jpg', 'wb')
            #data.write(response.body)
            self.upyun_client.setContentMD5(md5(response.body))
            #u = self.upyun_client.writeFile(image_key, data)
            u = self.upyun_client.writeFile(image_key, response.body)
            print u
            #data.close()
            self.log('save image to upyun: %s' % image_key)
        except Exception as e:
            self.log("exception: %s" % e, level=log.ERROR)
            import traceback
            self.log(traceback.format_exc(), level=log.ERROR)
            
    def _save_image(self, image_key, image_data):
        self.upyun_client.setContentMD5(md5(image_data))
        a = self.upyun_client.writeFile('/%s'%image_key,image_data)
        print a
        self.log("save image: %s " % image_key)

