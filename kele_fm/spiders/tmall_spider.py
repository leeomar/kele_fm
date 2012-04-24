#/bin/python
#coding: utf8

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.project import crawler
from scrapy.http import Request
from scrapy import log
from kele_fm.items import GoodsItem
from kele_fm.upyunapi.upyun import UpYun,md5,md5file
from kele_fm.spiders.categorizer import Categorizer
from kele_fm.spiders.dbclient import DBClient

class TmallSpider(BaseSpider):
    name = 'tmall.com'
    allowd_domains = ['tmall.com']
    start_urls = [
            'http://brand.tmall.com/tagValueIndex.htm?industryId=100&ftg=46&prt=1331861359023&prc=1'
            ]
    
    def __init__(self):
        self.upyun_client = UpYun('kele-img','kele-admin','omar1984')
        self.cgr = Categorizer()
        self.cgr.load('category.cfg', 'tags.cfg', 'words.dic')
        self.dbclient = DBClient()
        self.dbclient.open()

    def parse(self, response):
        self.log('parse %s, meta: %s' % (response.url, response.request.meta),\
                level=log.DEBUG)

        int_dep = response.request.meta.get("INT_DEP", None)
        req_type = response.request.meta.get("type", None)
        try:
            if req_type == 'image':
                self.log('process image, url:%s' % response.url,
                        level=log.DEBUG)
                #print response.headers
                directory='/tmall/%s' % response.request.meta.get('image_key')
                self.upyun_client.setContentMD5(md5(response.body)) 
                u = self.upyun_client.writeFile(directory, response.body,
                        auto=True)
                self.log('save image to upyun: %s, %s' % (directory, u))
            elif int_dep is None:
                self._process_entrypage(response)
            elif int_dep == 1:
                self._process_listpage(response)
                #for item in self._process_listpage(response):
                #    yield item
        except Exception as e:
            self.log("exception: %s" % e, level=log.ERROR)
            import traceback
            self.log(traceback.format_exc(), level=log.ERROR)
            
    def _process_entrypage(self, response):
        self.log("process entry page: %s" % response.url, level=log.DEBUG)
        #print response.body
        print response.encoding
        #response.body = response.body.decode("GBK").encode("utf8")
        hxs = HtmlXPathSelector(response)
        print hxs
        #brandlist_pattern = "//div[@class='brandList']/"
        brandlist_pattern = "//div[@class='brandList']/dl/dd"
        brandlist = hxs.select(brandlist_pattern)
        print hxs.select("//div[@class='brandList']")
        print brandlist
        for item in brandlist:
            links = item.select('a')
            for link in links:
                url = link.select('./@href').extract()
                brand = link.select('./@title').extract()
                print url, brand
                if url and brand:
                    meta = {'INT_DEP' : 1, 'from_url' : response.url,\
                            'brand' : brand[0]}
                    request = Request(url=url[0], meta = meta)
                    crawler.engine.crawl(request, self)
                    self.log('generate new request:%s' % url, level=log.DEBUG)
                else:
                    self.log('Error: url %s, brand %s' % \
                        (' '.join(url), ' '.join(brand)), level=log.ERROR)
    

    def _process_listpage(self, response):
        self.log("process list page: %s" % response.url, level=log.DEBUG)

        hxs = HtmlXPathSelector(response)
        
        #TODO: pagination
        nextpage = hxs.select("//a[@class='page-next']/@href")
        if nextpage:
            self.log('parse nextpage %s' % nextpage, level=log.DEBUG)
            nextpage = nextpage[0].extract()
            print nextpage
            meta ={'INT_DEP' : 1, 'from_url' : response.url, \
                    'brand' : response.request.meta.get('brand')}
            request = Request(url=nextpage, meta=meta)
            crawler.engine.crawl(request, self)
            self.log('nextpage %s' % nextpage, level=log.DEBUG)

        product_list = \
            hxs.select("//div[@id='J-listContainer']/form/ul[@class='product-list']/li")
        for item in product_list:
            product_info = item.select("div[@class='productInfo']")
            
            product_img = \
                product_info.select("div[@class='product-img']/a/img/@data-ks-lazyload").extract()
                #product_info.select("div[@class='product-img']/a/@href").extract()
            tmall_price = \
                product_info.select("p/strong[@class='tmall-price']/text()").extract()
            default_price = \
                product_info.select("p/del[@class='proDefault-price']/text()").extract()

            product_url = \
                product_info.select("h3[@class='product-title']/a/@href").extract()
            product_title = \
                product_info.select("h3[@class='product-title']/a/text()").extract()

            tag = \
                product_info.select("p[@class='product-attr']/a/text()").extract()
            if tag and len(tag) > 0:
                tag = tag[0].encode('utf-8')
            else:
                tag = ''

            goods_item = GoodsItem()
            goods_item['url'] = product_url[0].encode('utf-8')
            
            title = product_title[0].encode('utf-8')
            goods_item['title'] = title 
            goods_item['cat'] = self.cgr.get_category(title)
            extract_tag = self.cgr.get_tag(title)
            if len(extract_tag) > 0:
                tag = "%s %s" %(tag, extract_tag)
            
            image_url = None
            if product_img:
                image_url = self._normalize_image_url(product_img[0])

            if image_url:
                image_key = self._gen_image_key(image_url)
                goods_item['img'] = image_key.encode('utf-8') 
                self.crawl_image_request(image_key, image_url, response.url)
            else:
                goods_item['img'] = ""

            
            goods_item['price'] = int(float(tmall_price[0])*100)
            if default_price and len(default_price) > 0:
                goods_item['default_price'] = int(float(default_price[0])*100)
            else:
                goods_item['default_price'] = 0

            goods_item['tag'] = tag
            self.log('save new item: %s' % goods_item['url'])
            #self.log("generate new item: %s, %s, %s, %s, %s, %s" \
            #        % (goods_item['title'], goods_item['price'],\
            #        goods_item.get('default_price', None), goods_item['url'],\
            #        goods_item['img'], goods_item['tag']))

            self.dbclient.insert(goods_item)

    def _process_detailpage(self, response):
        pass

    def _gen_image_key(self, image_url):
        image_type = image_url.split('.')[-1]
        print "Image: %s, %s" %(image_url, image_type)
        return "%s.%s" % (md5(image_url), image_type)

    def _save_image(self, image_key, image_data):
        pass

    def _normalize_image_url(self, image_url):
        image_type = image_url.split('.')[-1]
        if image_type not in ('jpg', 'png'):
            self.log("bad image type:%s, url:%s" % (image_type, image_url),
                    level=log.ERROR)
            return None

        suffix = '_b.jpg'
        pos = image_url.rfind(suffix)
        if pos + len(suffix) == len(image_url):
            return image_url[0:pos]
        
        return image_url

    def crawl_image_request(self, image_key, image_url, source_url):
        meta = {'type' : 'image', 'image_key': image_key, 'from_url' :
                source_url}
        request = Request(url=image_url, meta=meta)
        crawler.engine.crawl(request, self)
        self.log('crawl new image request, key:%s, url:%s, source:%s' \
            %(image_key, image_url, source_url), level=log.DEBUG)
