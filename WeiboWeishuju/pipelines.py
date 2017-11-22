# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from WeiboWeishuju.items import *

class WeiboweishujuPipeline(object):
    def process_item(self, item, spider):
        return item


class CrawlerPipeline(object):
    def __init__(self):
        import codecs
        self.file = codecs.open('output.txt', mode='a', encoding='utf-8')


    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            self.file.write(('\t'.join(['{}'] * len(item)) + '\n').format(item['weibo_id'], item['nickname'], item['home_url'],
                                                                          item['weirenwu_followers_count'], item['weirenwu_is_appointment_account'], item['weirenwu_fans_top_status'],
                                                                          item['weirenwu_influence'], item['weirenwu_play_count'], item['weirenwu_direct_price'],
                                                                          item['weirenwu_repost_price'], item['weirenwu_accept_ratio_week'], item['weirenwu_category'],
                                                                          item['fetched_time']))
            self.file.flush()

    def finalize(self):
        self.file.close()
