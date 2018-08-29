# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class HouseGanjiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    s_address = Field()
    title = Field()
    price = Field()
    type = Field()
    space = Field()
    direction = Field()
    floor = Field()
    elevator = Field()
    decoration = Field()
    village = Field()
    subway = Field()
    address = Field()
    contact = Field()
    phone = Field()
    image = Field()