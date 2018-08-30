# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import pymysql

class HouseGanjiPipeline(object):
    def process_item(self, item, spider):
        return item

class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()
    def process_item(self, item, spider):
        if item['phone'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['phone'])  ##这里换成你自己的item["#"]
            return item


class MysqlPipeline():
    def __init__(self,host,database,user,password,port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            host = crawler.settings.get('MYSQL_HOST'),
            database =  crawler.settings.get('MYSQL_DATABASE'),
            user = crawler.settings.get('MYSQL_USER'),
            password = crawler.settings.get('MYSQL_PASSWORD'),
            port = crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self,spider):
        self.db = pymysql.connect(host=self.host,user=self.user,passwd=self.password,db=self.database,charset='utf8')
        self.cursor = self.db.cursor()

    def close_spider(self,spider):
        self.db.close()

    def process_item(self,item,spider):
            insert_sql = 'insert into spider_house(s_address,title,price,type,space,direction,floor,elevator,decoration,village,subway,address,contact,phone,image) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.cursor.execute(insert_sql,(item['s_address'],item['title'],item['price'],item['type'],item['space'],item['direction'],item['floor'],item['elevator'],item['decoration'],
                                            item['village'],item['subway'],item['address'],item['contact'],item['phone'],str(item['image'])))
            self.db.commit()
            return item
