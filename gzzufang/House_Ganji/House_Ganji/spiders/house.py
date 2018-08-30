# -*- coding: utf-8 -*-
import scrapy
from ..items import  HouseGanjiItem
import re
from scrapy.http import Request,FormRequest
from scrapy.linkextractor import LinkExtractor
import re
from urllib.parse import urlencode
import json
from json.decoder import  JSONDecodeError


class HouseSpider(scrapy.Spider):
    name = 'house'
    allowed_domains = ['ganji.com']

    all_city=[
        "chaoyang",
        "kaifeng",
        "nanyang",
        "zz",
        "puer",
    ]
    start_urls = [
        'http://{city}.ganji.com/fang1/a2/'.format(city = city) for city in all_city
    ]

    def __init__(self):
        self.count = 0
        self.max_count = 3    ##每一个页面最大爬取次数
        self.img_list=[]
        self.current_num = 0
        self.max_num = 6

    def parse(self, response):
        link = LinkExtractor(deny='/fang1/a2/',restrict_xpaths='//div[@class="f-filter f-w1190"]//dd[@class="info"]/div[@class="thr-list"]//li[@class="item"]/a')
        links = link.extract_links(response)
        for i in links:
            city_name = re.split('\/', i.url)[-3]
            yield Request(i.url, callback=self.get_index, meta={'city_name':city_name, 'dont_redirect': True,  'handle_httpstatus_list': [301, 302]},dont_filter=False)

    def get_index(self, response):
        city_name = response.meta['city_name']
        link = LinkExtractor(allow='/fang1/.*htm',restrict_xpaths='//div[@class="f-main f-clear f-w1190"]//div[@class="f-main-list"]/div[@class="f-list js-tips-list"]/div')
        links = link.extract_links(response)
        for i in links:
            city = re.split('\/|\.',i.url)[2]
            yield Request(i.url, callback=self.get_message, meta={'city':city,'city_name': city_name, 'dont_redirect': True,  'handle_httpstatus_list': [301, 302]},dont_filter=False)

    def get_message(self, response):
        city = response.meta['city']
        item = HouseGanjiItem()

        item['s_address'] = response.meta['city_name']
        item['title'] = response.xpath('//div[@class="card-info f-fr"]/div[@class="card-top"]/p[@class="card-title"]/i/text()').extract_first().strip()
        item['price'] = response.xpath('//ul[@class="card-pay f-clear"]/li[@class="price"]/span[@class="num"]/text()').extract_first().strip()
        item['type'] = "".join(response.xpath('//ul[@class="er-list f-clear"]/li[@class="item f-fl"]/span[contains(text(),"户")]/following-sibling::span//text()').extract())
        item['space'] ="".join(response.xpath('//ul[@class="er-list f-clear"]/li[@class="item f-fl"]/span[contains(text(),"面")]/following-sibling::span//text()').extract()).replace("\xa0&nbsp","")
        item['direction'] = "".join(response.xpath('//ul[@class="er-list f-clear"]/li[@class="item f-fl"]/span[contains(text(),"朝")]/following-sibling::span//text()').extract())
        item['floor'] = "".join(response.xpath('//ul[@class="er-list f-clear"]/li[@class="item f-fl"]/span[contains(text(),"楼")]/following-sibling::span//text()').extract())
        item['elevator'] = "".join(response.xpath('//ul[@class="er-list f-clear"]/li[@class="item f-fl"]/span[contains(text(),"电梯情况")]/following-sibling::span//text()').extract())
        item['decoration']="".join(response.xpath('//ul[@class="er-list f-clear"]/li[@class="item f-fl"]/span[contains(text(),"装修情况")]/following-sibling::span//text()').extract())
        self.subway = response.xpath('//ul[@class="er-list-two f-clear"]//div[@class="subway-wrap"]/span[@class="content"]/text()')
        if self.subway:
            item['subway'] = response.xpath('//ul[@class="er-list-two f-clear"]//div[@class="subway-wrap"]/span[@class="content"]/text()').extract_first().strip()
        else:
            item['subway'] = "no subway"
        item['address']="".join(response.css('div.card-info.f-fr > div.card-top > ul.er-list-two.f-clear > li:last-child ::text').extract()).strip().replace(" ","").replace("\n","").replace("\t","")
        item['village'] = re.split("共","".join(response.css('div.card-info.f-fr > div.card-top > ul.er-list-two.f-clear > li:nth-child(1) ::text').extract()).strip().replace(" ","").replace("\n","").replace('\t',""))[0]
        item['contact'] = response.xpath('//div[@class="card-user"]//div[@class="user-info-top"]/p[@class="name"]/text()').extract_first().strip()
            ##图片最多要六张
        for i in response.xpath('//div[@class="small-img"]/ul[@class="small-wrap f-clear"]//img/@src').extract():
            if self.current_num < self.max_num:
                self.img_list.append(i)
                self.current_num += 1
        item['image'] = self.img_list
        phone = response.xpath('//div[@class="card-info f-fr"]/div[@class="f-clear"]//div[@class="c_phone f-clear"]/@data-phone').extract_first()
        url = "http://%s.ganji.com/ajax.php?" % (city)
        ## 设置跳转页面数据
        formdata = {
            'dir': 'house',
            'module': 'secret_phone',
            'user_id': '736905901',
            'puid': '3479784040',
            'major_index': '1',
            'phone':str(phone),
            'isPrivate':'1',
        }
        url = url + urlencode(formdata)
        yield  Request(url,callback=self.get_phone,meta={'item':item,'dont_redirect': True},dont_filter=False)

    def get_phone(self,response):
        item =  response.meta['item']
        # print(response.url)
        # print(response.body)
        # if json.load(response.body_as_unicode()):
        #     item['phone'] = json.loads(response.body_as_unicode()).get('secret_phone')
        # else:
        #     item['phone'] = ""
        # yield item

        try:
            data = json.loads(response.body_as_unicode())
            if data and 'secret_phone' in data.keys():
                item['phone'] = json.loads(response.body_as_unicode()).get('secret_phone')
        except JSONDecodeError:
            pass

        yield item