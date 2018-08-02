#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen


try:
    from selenium.webdriver import Chrome, ChromeOptions
    from selenium.webdriver.common.keys import Keys
except ImportError:
    raise ImportError('您应该没有安装selenium或者Chrome驱动...\n请检查安装后再次执行。') 
from datetime import datetime
import time   


class Browser():
    '''
        使用selenium调用无头Chrome，获取需要执行js才能获取的RAIL_EXPIRATION和RAIL_DEVICEID。
        >>> browser = Browser()
        >>> browser.init()
        >>> browser.ticket_check('北京', '石家庄')  # 站名是随意的
        >>> cookie = browser.get_cookie()  # 返回的是一个包含cookie内容的python字典
    '''


    url_init = 'https://kyfw.12306.cn/otn/leftTicket/init'


    def __init__(self, flag='prod'):
        if flag == 'dev':  # 此时有头，方便调试
            opt = None
        elif flag == 'prod':
            opt = ChromeOptions()
            opt.set_headless()
        self.browser = Chrome(chrome_options=opt)


    def init(self, url=url_init):  
        self.browser.get(url)      

        
    def ticket_check(self, from_station, to_station, t=5):  # 模拟点击查票，这时自动访问logdevice
        '''
            params:
            :from_station:str, 随意一个始发站；
            :to_station:str, 随意一个到达站；
            :t:int, 延时，默认5秒。
        '''

        ts = 0
        while True:
            element_fs = self.browser.find_elements_by_id('fromStationText')
            element_ts = self.browser.find_elements_by_id('toStationText')
            element_ck = self.browser.find_elements_by_id('query_ticket')

            if element_fs and element_ts and element_ck:
                element_fs = element_fs[0]
                element_ts = element_ts[0]
                element_ck = element_ck[0]
                break
            
            ts += 1
            if ts == t:
                raise TimeoutError('网络貌似有点问题...T_T\n也可能是element id改变了。。。')
            time.sleep(1)

        element_fs.clear()
        element_fs.send_keys(from_station)
        element_fs.send_keys(Keys.ENTER)
        element_ts.clear()
        element_ts.send_keys(to_station)
        element_ts.send_keys(Keys.ENTER)
        element_ck.click()


    def get_cookie(self, t=5):  # 等待加载完成并返回cookie
        '''t为等待时间近似为秒'''

        ts = 0
        cookie = {}
        while True:
            cookies = self.browser.get_cookies()
            if cookies:
                for i in cookies:
                    if i['name'] not in cookie:
                        cookie[i['name']] = i['value']
                self.browser.quit()
                return cookie

            ts += 1
            if ts == t:
                raise TimeoutError('网络是不是出了问题？T_T或者返回的网页没有需要的cookie。')
            time.sleep(1)


if __name__ == '__main__':
    browser = Browser()
    browser.init()
    browser.ticket_check('北京','石家庄')
    cookie = browser.get_cookie()
    print(cookie)
