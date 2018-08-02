#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen


'''用于获取车票数据，格式化输出，并返回有效信息的python字典'''


import requests 


def __get_info_dict(date, from_station, to_station, cookie):  # 获取json数据，返回python字典
    '''date：xxxx-xx-xx,
       from_station:出发站，如BJP，
       to_station:到达站，如SJP
    '''

    url = 'https://kyfw.12306.cn/otn/leftTicket/query'
    payload = {
        'leftTicketDTO.train_date':'%s' % date,
        'leftTicketDTO.from_station':'%s' % from_station,
        'leftTicketDTO.to_station':'%s' % to_station,
        'purpose_codes':'ADULT',
    }
    header = {
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, br',
        'Cache-Control':'no-cache',
        'Connection':'keep-alive',   
        'Host':'kyfw.12306.cn',
        'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',
        'Pragma':'no-cache',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    }
    resp = requests.get(url, params=payload, headers=header, cookies=cookie)  #proxies={'http':'http://222.129.227.56:8118'})
    dic = resp.json()
    return dic


def __page_dict(dic):  # 提取需要信息，以一个二维python字典形式返回{'G1901':{...}, ...}
    dic_info = dict()
    l = dic['data']['result']
    for s in l:
        l = s.split('|')     
        if l[3][0] in ('K', 'Z', 'T'):
            dic_info[l[3]] = dict(secretStr=l[0], train_num=l[2], train_location=l[15], leftTicket=l[12], fromstation=l[6], tostation=l[7], ctime=l[8], dtime=l[9], atime=l[10], 软卧=l[23], 硬卧=l[28], 硬座=l[29], 无座=l[26])
        if l[3][0] in ('D', 'G'):
            dic_info[l[3]] = dict(secretStr=l[0], train_num=l[2], train_location=l[15], leftTicket=l[12], fromstation=l[6], tostation=l[7], ctime=l[8], dtime=l[9], atime=l[10], 特等商务座=l[32], 一等座=l[31], 二等座=l[30], 无座=l[26]) 
    return dic_info


def leftTicket_info(date, from_station, to_station, cookie):   # 返回车票信息的二维python字典{'1901':{...}, ...}
    '''
       获取指定日期，车站间的车票的余票信息，返回值为python字典。包含各火车信息的密文，车号，所属站，余票码，出发到达车站（与查询时可能会有不同），火车时间信息，余票信息。
       参数说明：
       data: xxxx-xx-xx;
       from_station: 出发车站, BJP;
       to_station: 到达站, SJP
    '''

    dic = __get_info_dict(date, from_station, to_station, cookie)
    info = __page_dict(dic)
    return info
    

def info_show(date, from_station, to_station, cookie):  # 格式化输出车票信息
    '''格式化输出余票信息，并返回一个火车信息的python字典{'G1901':{...},...}。from_station和to_station是由stationmap得到的英文简称，
       date格式类似于xxxx-xx-xx'''

    info = leftTicket_info(date, from_station, to_station, cookie)
    for k,v in info.items():
        txt = '商务座：%s，一等座：%s，二等座：%s，软卧：%s，硬卧：%s，软座：%s，硬座：%s，无座：%s\n'
        p = (v.get('特等商务座', '无'),v.get('一等座', '无'),v.get('二等座', '无'),v.get('软卧', '无'),v.get('硬卧', '无'),v.get('软座', '无'),v.get('硬座', '无'),v.get('无座', '无'))
        print(k + ':')
        print('始发时间：%s，到达时间：%s，全程：%s' % (v.get('ctime','-'), v.get('dtime','-'), v.get('atime', '-')))
        print(txt % p)
    return info   
    