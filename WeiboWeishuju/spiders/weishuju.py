# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver
import random
import logging
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from WeiboWeishuju.settings import  WEIBO_USERNAME, WEIBO_PASSWD, WEIBO_HEADERS,WEIBO_PATTERN
from WeiboWeishuju.items import WeiboItem


class WeishujuSpider(scrapy.Spider):
    name = "weishuju"
    cookies = {}
    allowed_domains = ["weibo.com"]
    driver = webdriver.PhantomJS()

    def start_requests(self):
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.resourceTimeout"] = 1000
        cap["phantomjs.page.settings.loadImages"] = True
        cap["phantomjs.page.settings.disk-cache"] = True
        self.driver.get('https://login.sina.com.cn/sso/login.php')
        time.sleep(2)
        username = self.driver.find_element_by_id('username')
        password = self.driver.find_element_by_id('password')
        submit = self.driver.find_elements_by_xpath('//*[@id="vForm"]/div[2]/div/ul/li[7]/div[1]/input')[0]
        username.send_keys(WEIBO_USERNAME)
        password.send_keys(WEIBO_PASSWD)
        submit.click()
        time.sleep(5)
        url = 'http://weirenwu.weibo.com/taskv2/index.php?c=task.addseluser'
        self.driver.get(url)
        time.sleep(2+random.random())
        cookie_list = self.driver.get_cookies()
        for cookie in cookie_list:
            self.cookies[cookie['name']] = cookie['value']
        print self.cookies
        yield scrapy.Request(url='http://weirenwu.weibo.com/taskv2/index.php?c=task.addseluser',
                      cookies=self.cookies,
                      headers=WEIBO_HEADERS,
                      callback=self.parse_dif2,
                      meta={'p': 1})


    def parse_dif2(self,response):
        fetched_time = int(time.time())
        tres = response.xpath('//table[@class="dsAttr_tbl"]//tr')
        print '函数dif2  爬取默认页'
        if len(tres) > 1:
            print '爬取默认转发页'
            for tr in tres[1:]:
                try:
                    item = WeiboItem()
                    item['nickname'] = tr.xpath('td[2]/a/text()').extract()[0]
                    item['home_url'] = tr.xpath('td[2]/a/@href').extract()[0]
                    text = tr.xpath('td[2]/span/@title').extract()
                    print text
                    if len(text) >= 1:
                        if u'1.该账号为预约账号' in text[0]:
                            item['weirenwu_is_appointment_account'] = 1
                        else:
                            item['weirenwu_is_appointment_account'] = 0
                    else:
                        item['weirenwu_is_appointment_account'] = 0
                    item['weibo_id'] = item['home_url'].split('/')[-1]
                    item['weirenwu_influence'] = int(len(tr.xpath('td[3]/span')))
                    if len(tr.xpath('td[4]/text()').extract()):
                        item['weirenwu_category'] = tr.xpath('td[4]/text()').extract()[0]
                    else:
                        item['weirenwu_category'] = 'None'
                    item['weirenwu_repost_price'] = float(tr.xpath('td[5]/span/text()').extract()[0].replace('¥', ''))
                    item['weirenwu_followers_count'] = int(tr.xpath('td[6]/text()').extract()[0].replace('万', '0000'))
                    item['weirenwu_play_count'] = int(re.findall('(?<=<td>)\d*(?=<)', tr.xpath('comment()').extract()[0])[0])
                    text1 = tr.xpath('td[7]/text()').extract()[0]
                    text1 = text1.replace('%','')
                    item['weirenwu_accept_ratio_week'] = float(int(text1) / 100)
                    if tr.xpath('td[8]/span/span/@class').extract()[0] == 'tbl_fenHot3':
                        item['weirenwu_fans_top_status'] = 0
                    else:
                        item['weirenwu_fans_top_status'] = 1
                    item['fetched_time'] = fetched_time
                    item['weirenwu_direct_price'] = -1
                    yield item
                except Exception as e:
                    logging.exception(e)
            yield scrapy.Request(url=WEIBO_PATTERN.format(response.meta['p'] + 1),
                                 cookies=self.cookies,
                                 headers=WEIBO_HEADERS,
                                 callback=self.parse_dif2,
                                 dont_filter=True,
                                 meta={'p': response.meta['p'] + 1})

        else:
            print '开始原创价目爬取'
            self.driver.get('http://weirenwu.weibo.com/taskv2/?c=task.taskList&action=ongoing')
            time.sleep(1)
            submit = self.driver.find_elements_by_xpath("//dt[@class='creatRwDt']/a")[0]
            submit.click()
            time.sleep(2)
            name = self.driver.find_element_by_id('taskname')
            text = self.driver.find_element_by_id('posttext')
            click = self.driver.find_element_by_id('btnnext')
            name.send_keys('21213232132')
            text.send_keys('jdjjdjdjjdj')
            click.click()
            cookie_list = self.driver.get_cookies()
            for cookie in cookie_list:
                self.cookies[cookie['name']] = cookie['value']
            print self.cookies
            print '模拟操作结束'
            yield scrapy.Request(url='http://weirenwu.weibo.com/taskv2/index.php?c=task.addseluser',
                                 cookies=self.cookies,
                                 headers=WEIBO_HEADERS,
                                 callback=self.parse_dif3,
                                 dont_filter=True,
                                 meta={'p': 1})

    def parse_dif3(self, response):
        fetched_time = int(time.time())
        trs = response.xpath('//table[@class="dsAttr_tbl"]//tr')
        print trs
        print '原创匹配xpath'
        if len(trs) > 1:
            print '进入原创爬去'
            for tr in trs[1:]:
                try:
                    item = WeiboItem()
                    item['nickname'] = tr.xpath('td[2]/a/text()').extract()[0]
                    item['home_url'] = tr.xpath('td[2]/a/@href').extract()[0]
                    text = tr.xpath('td[2]/span/@title').extract()
                    print text
                    if len(text) >= 1:
                        if u'1.该账号为预约账号' in text[0]:
                            item['weirenwu_is_appointment_account'] = 1
                        else:
                            item['weirenwu_is_appointment_account'] = 0
                    else:
                        item['weirenwu_is_appointment_account'] = 0
                    item['weibo_id'] = item['home_url'].split('/')[-1]
                    item['weirenwu_influence'] = int(len(tr.xpath('td[3]/span')))
                    if len(tr.xpath('td[4]/text()').extract()):
                        item['weirenwu_category'] = tr.xpath('td[4]/text()').extract()[0]
                    else:
                        item['weirenwu_category'] = 'None'
                    item['weirenwu_direct_price'] = float(tr.xpath('td[5]/span/text()').extract()[0].replace('¥', ''))
                    item['weirenwu_repost_price'] = -1
                    item['weirenwu_followers_count'] = int(tr.xpath('td[6]/text()').extract()[0].replace('万', '0000'))
                    item['weirenwu_play_count'] = int(re.findall('(?<=<td>)\d*(?=<)', tr.xpath('comment()').extract()[0])[0])
                    text1 = tr.xpath('td[7]/text()').extract()[0]
                    text1 = text1.replace('%','')
                    item['weirenwu_accept_ratio_week'] = float(int(text1)/100)
                    if tr.xpath('td[8]/span/span/@class').extract()[0] == 'tbl_fenHot3':
                        item['weirenwu_fans_top_status'] = 0
                    else:
                        item['weirenwu_fans_top_status'] = 1
                    item['fetched_time'] = fetched_time
                    yield item
                except Exception as e:
                    logging.exception(e)
            yield scrapy.Request(url=WEIBO_PATTERN.format(response.meta['p'] + 1),
                                 cookies=self.cookies,
                                 headers=WEIBO_HEADERS,
                                 callback=self.parse_dif3,
                                 dont_filter=True,
                                 meta={'p': response.meta['p'] + 1})
        else:
            self.driver.quit()




