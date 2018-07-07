#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen

# from station_map import StationMap
# from get_leftticket_info import leftTicket_info
from datetime import datetime
import requests
import random
import time
import json
import re


class BookingSimulator(object):

    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control':'no-cache',
        'Connection':'keep-alive',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Host':'kyfw.12306.cn',
        'Pragma':'no-cache',
        'X-Requested-With':'XMLHttpRequest',
    }


    def __init__(self, username, password, from_station, to_station, date):
        '''username：12306账户，password：登陆密码， from_station：出发站，to_station：到达站，date：日期（xxxx-xx-xx)'''

        self.username = username
        self.password = password
        self.from_station = StationMap.get_dict().get(from_station)
        self.to_station = StationMap.get_dict().get(to_station)
        self.date = date
        self.session = requests.Session()
        

    # def ticket_info(self):
    #     ticket_dic = leftTicket_info(self.date, self.from_station, self.to_station)
    #     for k,v in ticket_dic.items():
    #         txt = ''' %s: 无座:%s,  硬座:%s,  软座:%s,  硬卧:%s,  软卧:%s,  二等座:%s,  一等座:%s,  商务/特等座:%s。'''
    #         print(txt % (k, v.get('无座',' '),v.get('硬座',' '),v.get('软座',' '),v.get('硬卧',' '),v.get('软卧',' '),v.get('二等座',' '),v.get('一等座',' '),v.get('特等商务座',' ')))

    
    def checkUser(self):  # 请求返回cookie值中的BIGipServerotn, JESSIONID, route,字典形式
        '''请求第一步，请求cookie包括_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en),_jc_save_toDate(today)，
           _jc_save_toStation,_jc_save_wfdc_flag:dc。返回cookie，BIGipServerotn, JSESSIONID, route的字典'''
  
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        try:
            resp = self.session.post(url=url, headers=self.header, data={'_json_att':''})
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] is 'true':
                print('__checkUser成功...')
                return resp.cookies.get_dict()
            else:
                print('__checkUser出现错误，返回status不是true！')            
        except Exception as e:
            print('__checkUser出错：%s' % e)

    
    def captcha_image(self, cookie):  # 获取验证码，请求cookie中需要BIGipServerotn，route。返回cookie包括_passport_ct, _passport_session ,_BIGipServerpool_passport
        '''请求cookie中需要_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en),_jc_save_toDate(today)，
           _jc_save_toStation,_jc_save_wfdc_flag:dc, BIGipServerotn，route。返回cookie包括_passport_ct, 
           _passport_session ,_BIGipServerpool_passport, 函数返回图片，cookie字典'''

        url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&{}'
        payload = {
            'login_site':'E',
            'module':'login',
            'rand':'sjrand',
        }
        try:
            resp = self.session.get(url=url.format(random.random()), headers=self.header, cookies=cookie, params=payload)
            resp.raise_for_status
            print('__captcha_image获取到验证图片...')
            return resp.content, resp.cookies.get_dict()  # 返回验证码（二进制），响应cookie。
        except Exception as e:
            print('__captcha_image获取验证图片时出错：%s' % e)


    def captcha_check(self, position, cookie):  # 验证验证码，position为验证码识别的位置，请求cookie需要_passport_ct, _passport_sessionn, BIGipServerotn, BIGipServerpool_passport, route
        '''请求cookie需要_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en), _jc_save_toDate(today)，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, _passport_ct, _passport_session, BIGipServerotn, 
           BIGipServerpool_passport, route'''

        url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        data = {
            '_json_att':'',
            'answer':','.join(map(str, position)),
            'login_site':'E',
            'rand':'sjrand',
        }
        try:
            resp = self.session.post(url=url, headers=self.header, data=data)
            jsn = resp.json()
            return jsn['result_code']  # 值为4时识别成功
        except Exception as e:
            print('__captcha_check验证码检验错误：%s' % e)


    def login(self, cookie):  # 登陆，请求cookie需要_passport_ct, _passport_session, BIGipServerotn, BIGipServerpool_passport, route。返回的cookie取消_passport_ct, 设置uamtk,响应值为uamtk
        '''请求cookie需要_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en), _jc_save_toDate(today)，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, _passport_ct, _passport_session, BIGipServerotn, 
           BIGipServerpool_passport, route。返回cookie，取消_passport_ct，新增uamtk'''

        url = 'https://kyfw.12306.cn/passport/web/login'
        data = {
            '_json_att':'',
            'appid':'otn',
            'password':self.password,
            'username':self.username,
        }
        try:
            resp = self.session.post(url=url, headers=self.header, data=data, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['result_code'] is '0':
                uamtk = jsn['uamtk']
                print('%s' % jsn['result_message'])
                return uamtk  # 返回uamtk，用于下步设置cookie
            else:
                print('__login出现某些错误...')
        except Exception as e:
            print('登陆出现错误：%s' % e)


    def uamtk(self, cookie):  # 请求cookie包括_passport_session, BIGipServerotn, BIGipServerpool_passport, route, uamtk（来自上一步）。返回结果为包含newapptk即tk的字符串（一个js表达式）
        '''请求cookie需要_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en), _jc_save_toDate(today)，
           _jc_save_toStation, _jc_save_wfdc_flag:dc,  _passport_session, BIGipServerotn, 
           BIGipServerpool_passport, route, uamtk。响应返回带有tk的json'''

        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        payload = {
            'callback':'jQuery19108285060857122477_%s' % int(time.time()*1000),
        }
        data = {
            '_json_att':'',
            'appid':'otn',
        }
        try:
            resp = self.session.post(url, headers=self.header, params=payload, data=data, cookies=cookie)
            resp.raise_for_status
            string = resp.text
            if re.search(r'"result_code":(\w)', string).group(1) is '4':
                tk = re.search(r'"newapptk":"(.*?)"', string).group(1)
                print('获取uamtk成功！')
                return tk  # 与tk值相同
            else:
                print('__uamtk出现某些错误...')
        except Exception as e:
            print('获取uamtk时出错：%s' % e)


    def uamauthclient(self, cookie, tk):  # 请求cookie需要BIGipServerotn, BIGipServerpool_passport, JSESSIONID, route。返回cookie包括tk与之前newapptk相同
        '''请求cookie需要_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en), _jc_save_toDate(today)，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, JSESSIONID,
           route。响应带有tk值，返回cookie中也设置tk值'''

        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        data = {
            '_json_att':'',
            'tk': tk,
        }
        try:
            resp = self.session.post(url, headers=self.header, data=data, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['result_code'] is '0':
                apptk = jsn['apptk']
                print('%s' % jsn['result_message'])
                return apptk  # 与上步得到的tk值相同
            else:
                print('__uamauthclient出现错误！')
        except Exception as e:
            print('__uamauthclient出错：%s' % e)


    def submitOrderRequest(self, from_station, to_station, secretStr, cookie):  # 请求cookie包括BIGipServerotn, BIGipServerpool_passport, JSESSIONID, route, tk
        '''请求cookie需要_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en), _jc_save_toDate(today)，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, JSESSIONID,
           route，tk值。'''

        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {
            'back_train_data':datetime.today().strftime('%Y-%m-%d'),
            'purpose_codes':'ADULT',
            'query_from_station_name':from_station,
            'query_to_station_name':to_station,
            'secretStr':secretStr,  # 火车信息中secretStr
            'tour_flag':'dc',
            'train_date':self.date,
            'undefined':'',
        }
        try:
            resp = self.session.post(url, headers=self.header, data=data, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] is 'true':
                print('__submitOrderRequest成功...')
            else:
                print('__submitOrderRequest出现某些错误！')
        except Exception as e:
            print('__submitOrderRequest出错：%s' % e)


    def initDc(self, cookie):  # 请求cookie需要BIGipServerotn, BIGipServerpool_passport, JSESSIONID, roure, tk。响应对象包含了submittoken
        '''请求cookie需要_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en), _jc_save_toDate(today)，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, JSESSIONID,
           route，tk值。响应中提取token'''

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = {
            '_json_att':'',
        }
        try:
            resp = self.session.post(url, headers=self.header, data=data, cookies=cookie)
            resp.raise_for_status
            html = resp.text
            submittoken = re.search(r"globalRepeatSubmitToken = '(.*?)'", html).group(1)
            print('__initDc成功...')
            return submittoken
        except Exception as e:
            print('__initDc获取token时出错：%s' % e)


    def getPassengerDTOs(self, token, cookie):  # 请求cookie包含BIGipServerotn, BIGipServerpool_passport, JSESSIONID, route,tk。参数REPEAT_SUBMIT_TOKEN=之前获取的submittoken
        '''请求cookie需要_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en), _jc_save_toDate(today)，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, JSESSIONID,
           route，tk值。'''

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {
            '_json_att':'',
            'REPEAT_SUBMIT_TOKEN':token,
        }
        try:
            resp = self.session.post(url, data=data, headers=self.header, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] is 'true':
                dtos = jsn['data']['normal_passengers']
                print('__getPassengerDTOs获得联系人信息...')
                return dtos  # 个人信息的字典列表
            else:
                print('__getPassengerDTOs出现某些错误！')
        except Exception as e:
            print('获取乘客信息出错：%s' % e)


    def logdevice(self, cookie):  # 请求cookie包括BIGipServerotn, BIGipServerpool_passport, JSESSIONID, route, 提交车票需要的参数exp和dfp。
        '''请求cookie需要_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en), _jc_save_toDate(today)，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, JSESSIONID,
           route，tk值。'''

        url = 'https://kyfw.12306.cn/otn/HttpZF/logdevice'
        payload = {
            'oaew':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'algID':'ldk3m3czj2',
            'custID':'133',
            'dzuS':'0',
            'E3gR':'c533dba403bff9629dcefe49c81b1d33',
            'EOQP':'2e3118d565c7ff7fc669ee0fea13ce9b',
            'FMQw':'0',
            'Fvje':'i1l1s1',
            'hAqN':'Win64',
            'hashCode':'CgKHe9SFI8hRlyOOLGIV5Ojt1TsEjoaklO-EtYdascc',
            'jp76':'d41d8cd98f00b204e9800998ecf8427e',
            'ks0Q':'d41d8cd98f00b204e9800998ecf8427e',
            'IEnu':'3232236295',
            'platform':'WEB',
            'q4f3':'zh-CN',
            'q5aJ':'-8',
            'TeRS':'824x1536',
            'timestamp':str(int(time.time()*1000)),
            'tOHY':'824x1536',
            'VEek':'824x1536',
            'VPIf':'1',
            'VySQ':'824x1536',
            'wNLf':'824x1536',
            'yD16':'0',
        }
        try:
            resp = self.session.get(url, params=payload, cookies=cookie)
            resp.raise_for_status
            html = resp.text
            exp = re.search(r'"exp":"(.*?)"', html).group(1)
            dfp = re.search(r'"dfp":"(.*?)"', html).group(1)
            print('__logdevice成功...')
            return exp, dfp
        except Exception as e:
            print('__logdevice出错：%s' % e)


    def getPassCodeNew(self, cookie):  # 获取current_captcha_type
        '''请求cookie包括,_jc_save_fromDate(move time),_jc_save_fromStation(tuple,zn,en),_jc_save_toDate(today)
           ,_jc_save_toStation,_jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport,
           JSESSIONID, RAIL_DEVICEID=dfp, RAIL_EXPIRATION=exp, route, tk'''

        url = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp&{0}'
        try:
            resp = self.session.get(url, headers=self.header, cookies=cookie)
            resp.raise_for_status
            current_captcha_type = resp.cookies.get_dict()['current_captcha_type']
            return current_captcha_type
        except Exception as e:
            print('获取current_captcha_type出现错误：%s' % e)


    def checkOrderInfo(self, cookie, passenger_info, token ):  # 请求重新设置了tk值
        '''请求cookie包括,_jc_save_fromDate(move time),_jc_save_fromStation(tuple,zn,en),_jc_save_toDate(today)
           ,_jc_save_toStation,_jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, current_captcha_type,
           JSESSIONID, RAIL_DEVICEID=dfp, RAIL_EXPIRATION=exp, route, tk'''
        
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data = {
            '_json_att':'',
            'bed_level_order_num':'000000000000000000000000000000',
            'cancel_flag':'2',
            'oldPassengerStr':'%s,1,%s,,1_' % (passenger_info['passenger_name'], passenger_info['passenger_id_no']),
            'passengerTicketStr':'O,0,1,%s,1,%s,%s,N' % (passenger_info['passenger_name'], passenger_info['passenger_id_no'], passenger_info['mobile_no']),
            'randCode':'',
            'REPEAT_SUBMIT_TOKEN':token,
            'tour_flag':'dc',
            'whatsSelect':'1',
        }
        try:
            resp = self.session.post(url, headers=self.header, cookies=cookie, data=data)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] is 'true':
                print('__checkOrderInfo完成！')
                return resp.cookies.get_dict()['tk']
            else:
                print('__checkOrderInfo出现一些问题！')
        except Exception as e:
            print('__checkOrderInfo出现错误：%s' % e)


    def getQueueCount(self, cookie, train_info, from_station, to_station, date, token):  # 获取选定车票余票信息 trian_info是一个二维字典{1：{1：2}} from_station, to_station拼音大写简写
        '''请求cookie包括,_jc_save_fromDate(move time),_jc_save_fromStation(tuple,zn,en),_jc_save_toDate(today)
           ,_jc_save_toStation,_jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, current_captcha_type,
           JSESSIONID, RAIL_DEVICEID=dfp, RAIL_EXPIRATION=exp, route, tk'''

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        train_tuple = train_info.popitem()
        if train_tuple[0][0] in ('G', 'D'):
            if train_tuple[1]['二等座'] not in ('无', '', ' ', None):
                seatType = 'O'
            elif train_tuple[1]['一等座'] not in ('无', '', ' ', None):
                seatType = 'M'
        else:
            raise ValueError('目前只支持动车高铁的一等二等座自动订票')
        data = {
            '_json_att':'',
            'fromStationTelecode':from_station,
            'leftTicket':train_tuple[1]['leftTicket'],
            'purpose_code':'00',
            'REPEAT_SUBMIT_TOKEN':token,
            'seatType':seatType,
            'stationTrainCode':train_tuple[0],
            'toStationTelecode':to_station,
            'train_date':datetime.strptime(date, '%Y-%m-%d').strftime('%a+%b+%d+%Y+00:00:00+GMT+0800'),
            'train_location':train_tuple[1]['train_location'],
            'train_no':train_tuple[1]['train_no'],
        }
        try:
            resp = self.session.post(url, headers=self.header, cookies=cookie, data=data)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] is 'true':
                print('__getQueueCount成功！')
                return seatType
        except Exception as e:
            print('__getQueueCount出错：%s' % e)


    def confirmSingleForQueue(self, cookie, passenger_info, train_info, seatType, token):
        '''参数key_check_isChange全部由0-9，A-F组成，应该是一组十六进制字符串, 之前的js函数应该有一个toString()函数
           请求cookie包括,_jc_save_fromDate(move time),_jc_save_fromStation(tuple,zn,en),_jc_save_toDate(today)
           ,_jc_save_toStation,_jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, current_captcha_type,
           JSESSIONID, RAIL_DEVICEID=dfp, RAIL_EXPIRATION=exp, route, tk
        '''

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data = {
            '_json_att':'',
            'choose_seats':'',
            'dwAll':'N',
            'Key_check_isChange':''.join('%02X' % random.randint(0,255) for i in range(28)),
            'leftTicketStr':train_info.popitem()[1]['leftTicket'],
            'oldPassengerStr':'%s,1,%s,1_' % (passenger_info['passenger_name'], passenger_info['passenger_id_no']),
            'passengerTicketStr':'%s,0,1,%s,1,%s,%s,N' % (seatType, passenger_info['passenger_name'], passenger_info['passenger_id_no'],passenger_info['mobile_no']),
            'purpose_codes':'00',
            'randCode':'',
            'REPEAT_SUBMIT_TOKEN':token,
            'roomType':'00',
            'seatDetailType':'000',
            'train_location':train_info['train_location'],
            'whatsSelect':'1',
        }
        try:
            resp = self.session.post(url, data=data, headers=self.header, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] is 'true':
                print('__confirmSingleForQueue成功！')
        except Exception as e:
            print('__confirmSingleForQueue出错：%s' % e)
            

    def queryOrderWaitTime(self, cookie, token):  # 该方法需要循环访问，直至waitTime=-1，waitCount=0,orderld!='null'为止
        '''参数key_check_isChange全部由0-9，A-F组成，应该是一组十六进制字符串, 之前的js函数应该有一个toString()函数
           请求cookie包括,_jc_save_fromDate(move time),_jc_save_fromStation(tuple,zn,en),_jc_save_toDate(today)
           ,_jc_save_toStation,_jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, current_captcha_type,
           JSESSIONID, RAIL_DEVICEID=dfp, RAIL_EXPIRATION=exp, route, tk
        '''

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
        payload = {
            '_json_att':'',
            'random':str(int(time.time()*1000)),
            'REPEAT_SUBMIT_TOKEN':token,
            'tourFlag':'dc',
        }
        try:
            while True:
                resp = self.session.get(url, headers=self.header, cookies=cookie, params=payload)
                resp.raise_for_status
                jsn = resp.json()
                if jsn['data']['waitTime'] is '-1':
                    print('已成功订票，请于30分钟内到12306网站对应账号完成支付，逾期作废！')
        except Exception as e:
            print('__queryOrderWaitTime出错：%s' % e)
