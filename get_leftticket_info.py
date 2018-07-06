#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen

import requests 
import json

url = 'https://kyfw.12306.cn/otn/leftTicket/query'

def get_info_dict(data, from_station, to_station):  # 获取余票数据
    payload = {
        'leftTicketDTO.train_date':'%s' % data,
        'leftTicketDTO.from_station':'%s' % from_station,
        'leftTicketDTO.to_station':'%s' % to_station,
        'purpose_codes':'ADULT',
    }
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    }
    resp = requests.get(url, params=payload, headers=header)
    jsn = resp.text
    dic = json.loads(jsn)
    return dic

def page_dict(dic):  # 余票数据解析
    dic_info = dict()
    l = dic.get('data').get('result')
    for s in l:
        l = s.split('|')     
        if l[3][0] in ('K', 'Z', 'T'):
            dic_info[l[3]] = dict(secretStr=l[0], tain_nun=l[2], train_location=l[15], leftTicket=l[12], 软卧=l[23], 硬卧=l[28], 硬座=l[29], 无座=l[26])
        if l[3][0] in ('D', 'G'):
            dic_info[l[3]] = dict(secretStr=l[0], tain_num=l[2], train_location=l[15], leftTicket=l[12], 特等商务座=l[32], 一等座=l[31], 二等座=l[30], 无座=l[26]) 
    return dic_info

def leftTicket_info(data, from_station, to_station):
    '''
       获取指定日期，车站间的车票的余票信息，返回值为python字典。
       参数说明：
       data: str, 格式为：Y-M-D;
       from_station: str, 出发车站名类似'BJP', 与官方相同；
       to_station: 与from_station格式相同。
    '''

    dic = get_info_dict(data, from_station, to_station)
    info = page_dict(dic)
    return info
    

if __name__ == '__main__':
    dic = leftTicket_info('2018-07-08', 'BJP', 'SJP')
    print(len(dic))