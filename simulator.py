#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen


from station_map.get_map import StationMap
from get_leftticket_info import info_show
from datetime import datetime
from captchaRec import rec_run
from urllib import parse
import requests
import random
import time
import re


class BookingSimulator(object):
    
    # 用于initDC之前
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, br',
        'Cache-Control':'no-cache',
        'Connection':'keep-alive',    
        'Host':'kyfw.12306.cn',
        'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',
        'Pragma':'no-cache',
    }
    # 用于init
    header1 = header.copy()
    header1.update({'Referer':'https://kyfw.12306.cn/otn/queryOrder/initNoComplete'})
    # 用于initDC之后
    header2 = header.copy()
    header2.update({'Referer':'https://kyfw.12306.cn/otn/confirmPassenger/initDC'})

    map_dict = StationMap()  # 字典形式的车站地图key为中文站名，value为英文简写

    def __init__(self, username, password, from_station, to_station, date):
        '''username：12306账户，password：登陆密码， from_station：出发站，to_station：到达站，date：日期（xxxx-xx-xx)'''

        self.username = username
        self.password = password
        self.from_station = self.map_dict[from_station]  #英简大写
        self.to_station = self.map_dict[to_station]  # 英简大写
        self.from_station_cn = from_station
        self.to_station_cn = to_station
        self.date = date
        self._jc_save_fromdate = date
        self._jc_save_fromstation = self.__chchar('%s,%s' % (from_station, self.from_station))  # cookie中要用，所以先编码一边传输
        self._jc_save_todate = datetime.today().strftime('%Y-%m-%d')  # 单程时为订票当天
        self._jc_save_tostation = self.__chchar('%s,%s' % (to_station, self.to_station))
        self.session = requests.Session()

    
    def __chchar(self,string):  # 格式化cookie中带有中文的字符
        s = ascii(string).replace("'",'').upper()
        s = parse.quote(s).replace('%5CU','%u')
        return s


    # def init(self):
    #     '''请求第一步，返回cookie中的BIGipServerotn, JSESSIONID, route。'''

    #     url = 'https://kyfw.12306.cn/otn/leftTicket/init'
    #     try:
    #         resp = self.session.get(url, headers=self.header1)
    #         resp.raise_for_status
    #         cookie = resp.cookies.get_dict()
    #         # if 'BIGipServerotn' in cookie & 'JSESSIONID' in cookie & 'route' in cookie:
    #         print('成功创建会话！\n')
    #         print(cookie)
    #         return cookie
    #         # else:
    #         #     print('返回参数不全，请重试！\n')
    #         #     return False
    #     except Exception as e:
    #         print('__init()初始化错误:%s\n'%e)
    #         return False


    # def logdevice(self, cookie):
    #     '''请求cookie:_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
    #        _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, JSESSIONID, route。
    #        响应值中：exp = RAIL_EXPIRATION, dfp = RAIL_DEVICEID。'''

    #     url = 'https://kyfw.12306.cn/otn/HttpZF/logdevice'
    #     payload = {
    #         'oaew':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    #         'algID':'ldk3m3czj2',  # 在https://kyfw.12306.cn/otn/HttpZF/GetJS正则表达式可以得到
    #         'custID':'133',
    #         'dzuS':'0',
    #         'E3gR':'c533dba403bff9629dcefe49c81b1d33',
    #         'EOQP':'2e3118d565c7ff7fc669ee0fea13ce9b',
    #         'FMQw':'0',
    #         'Fvje':'i1l1s1',
    #         'hAqN':'Win64',
    #         'hashCode':'CgKHe9SFI8hRlyOOLGIV5Ojt1TsEjoaklO-EtYdascc',  #变参数 getjs中生成
    #         'jp76':'d41d8cd98f00b204e9800998ecf8427e',
    #         'ks0Q':'d41d8cd98f00b204e9800998ecf8427e',
    #         'IEnu':'3232236295',
    #         'platform':'WEB',
    #         'q4f3':'zh-CN',
    #         'q5aJ':'-8',
    #         'TeRS':'824x1536',
    #         'timestamp':str(int(time.time()*1000)),
    #         'tOHY':'24xx824x1536',
    #         'VEek':'unspecified',
    #         'VPIf':'1',
    #         'wNLf':'99115dfb07133750ba677d055874de87',  # 变参数getjs中生成
    #         'yD16':'0',
    #     }
    #     try:
    #         resp = self.session.get(url, headers = self.header, params=payload, cookies=cookie)
    #         resp.raise_for_status
    #         html = resp.text
    #         exp = re.search(r'"exp":"(.*?)"', html).group(1)
    #         dfp = re.search(r'"dfp":"(.*?)"', html).group(1)
    #         print('设备验证通过！\n')
    #         return exp, dfp
    #     except Exception as e:
    #         print('设备验证出错：%s\n' % e)
    #         return False

    
    def checkUser(self, cookie):
        '''请求第一步，请求cookie包括_jc_save_fromDate(出发时间), _jc_save_fromStation(tuple,zn,en),_jc_save_toDate(today)，
           _jc_save_toStation,_jc_save_wfdc_flag:dc。返回cookie，BIGipServerotn, JSESSIONID, route的字典。'''
  
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        try:
            resp = self.session.post(url=url, headers=self.header, cookies=cookie, data={'_json_att':''})
            resp.raise_for_status
            jsn = resp.json()
            if jsn['data']['flag'] == False:
                print('您还没登陆系统！\n')
                return False
            elif jsn['data']['flag'] == True:
                print('您已成功登陆系统！\n')
                return True 
        except Exception as e:
            print('检查登陆状态出错：%s' % e)
            print(jsn, '\n')
            return False
    

    def captcha_image(self, cookie):  # 获取验证码图片
        '''请求cookie:_jc_save_fromDate, _jc_save_fromStation,_jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn，route,
           RAIL_DEVICEID, RAIL_EXPIRATION。
           返回cookie：_passport_ct, _passport_session, BIGipServerpool_passport。 
           函数返回图片二进制对象和cookie字典。'''

        url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand'
        try:
            resp = self.session.get(url=url, headers=self.header, cookies=cookie)
            resp.raise_for_status
            if len(resp.content) > 5120:
                print('获取到验证图片!\n')
                return resp.content, resp.cookies.get_dict()  # 返回验证码（二进制），响应cookie。
            else:
                print('获得的验证码有误...\n')
                return False
        except Exception as e:
            print('获取验证图片时出错：%s\n' % e)
            return False


    def captcha_check(self, position, cookie):  # 验证验证码，验证码成功才能登陆。
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, _passport_ct, _passport_session, 
           BIGipServerotn, BIGipServerpool_passport, RAIL_DEVICEID, RAIL_EXPIRATION, route。
           参数position是以逗号隔开的图片位置的字符串。'''

        url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        data = {
            '_json_att':'',
            'answer':position,
            'login_site':'E',
            'rand':'sjrand',
        }
        try:
            resp = self.session.post(url=url, headers=self.header, cookies=cookie, data=data)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['result_code'] is '4':
                print(jsn['result_message'], '\n')
                return True
            else:
                print(jsn, '\n')
                return False
        except Exception as e:
            print('验证码检验错误：%s' % e)
            print(jsn, '\n')
            return False


    def login(self, cookie):   # 用户登陆，获取uamtk
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, _passport_ct, _passport_session, 
           BIGipServerotn, BIGipServerpool_passport, RAIL_DEVICEID, RAIL_EXPIRATION, route。
           返回值包含uamtk, 将添加到umatk的请求cookie中。'''

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
            if jsn['result_code'] is 0:
                uamtk = jsn['uamtk']
                print(jsn['result_message'], '\n')
                return uamtk  # 返回uamtk，用于下步设置cookie
            else:
                print('登陆有误！')
                print(jsn, '\n')
                return False
        except Exception as e:
            print('登陆时出现错误：%s' % e)
            print(jsn, '\n')
            return False


    def uamtk(self, cookie):  # 获取tk
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, _passport_session, BIGipServerotn, 
           BIGipServerpool_passport, RAIL_DEVICEID, RAIL_EXPIRATION, route, uamtk。
           返回带有tk的字符串。'''

        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        s = str(random.random())       
        payload = {
            'callback':'jQuery1910%s_%s' % (s[2:],int(time.time()*1000)),  
        }
        data = {
            '_json_att':'',
            'appid':'otn',
        }
        try:
            resp = self.session.post(url, headers=self.header, params=payload, data=data, cookies=cookie)
            resp.raise_for_status
            string = resp.text
            tk = re.search(r'"newapptk":"(.*?)"', string).group(1)
            if tk:
                print('获取tk成功！\n')
                return tk
            else:
                print('没能获取到tk！')
                print(string, '\n')
                return False
        except Exception as e:
            print('获取tk时出错：%s\n' % e)
            return False


    def uamauthclient(self, cookie, tk):
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route。
           参数tk POST到服务器，并在下次请求中添加到cookie中。'''

        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        data = {
            '_json_att':'',
            'tk': tk,
        }
        try:
            resp = self.session.post(url, headers=self.header, data=data, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['result_code'] == 0:
                print(jsn['result_message'], '\n')
                return True
            else:
                print('验证tk出错！')
                print(jsn, '\n')
                return False
        except Exception as e:
            print('__uamauthclient出错：%s' % e)
            print(jsn, '\n')
            return False


    def submitOrderRequest(self, train_info, cookie):
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route, tk。'''

        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {
            'back_train_date':self._jc_save_todate,
            'purpose_codes':'ADULT',
            'query_from_station_name':self.from_station_cn,
            'query_to_station_name':self.from_station_cn,
            'secretStr':parse.unquote(train_info['secretStr']),  # 火车信息中secretStr，必须由unquote编码
            'tour_flag':'dc',
            'train_date':self.date,
            'undefined':'',
        }
        try:
            resp = self.session.post(url, headers=self.header.update({'Referer':'https://kyfw.12306.cn/otn/leftTicket/init'}), data=data, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] is True:
                print('提交命令请求成功！\n')
                return True
            else:
                print('提交出现某些错误！')
                print(jsn, '\n')
                return False
        except Exception as e:
            print('__submitOrderRequest提交出错：%s' % e)
            print(jsn, '\n')
            return False


    def initDc(self, cookie):  # 为了提取token，key_check_isChange
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route, tk。
           响应中提取token'''

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = {
            '_json_att':'',
        }
        try:
            resp = self.session.post(url, headers=self.header, data=data, cookies=cookie)
            resp.raise_for_status
            html = resp.text
            submittoken = re.search(r"globalRepeatSubmitToken = '(.*?)'", html).group(1)
            Key_check_isChange = re.findall(r"'key_check_isChange':'(.*?)'", html)[0]
            print('获取token成功！\n')
            return submittoken, Key_check_isChange
        except Exception as e:
            print('获取token时出错：%s\n' % e)
            return False


    def getPassengerDTOs(self, cookie, token):  # 仅用于获取账户中的乘客信息，也可以自己构造信息提交
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route, tk。'''

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {
            '_json_att':'',
            'REPEAT_SUBMIT_TOKEN':token,
        }
        try:
            resp = self.session.post(url, data=data, headers=self.header2, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] is True:
                dtos = jsn['data']['normal_passengers']
                print('成功获得联系人信息！\n')
                return dtos  # 个人信息的字典列表
            else:
                print('获取联系人时出现某些错误！')
                print(jsn, '\n')
                return False
        except Exception as e:
            print('获取乘客信息出错：%s\n' % e)
            return False


    def getPassCodeNew(self, cookie):  # 获取current_captcha_type
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route, tk。'''

        url = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp&{0}'
        try:
            resp = self.session.get(url.format(str(random.random())), headers=self.header2, cookies=cookie)
            resp.raise_for_status
            current_captcha_type = resp.cookies.get_dict()['current_captcha_type']
            print('获得当前验证状态！\n')
            return current_captcha_type
        except Exception as e:
            print('获取current_captcha_type出现错误：%s\n' % e)
            return False

    def checkOrderInfo(self, seatType, cookie, passenger_info, token ):
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           current_captcha_type, JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route, tk。'''
        
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data = {
            '_json_att':'',
            'bed_level_order_num':'000000000000000000000000000000',
            'cancel_flag':'2',
            'oldPassengerStr':'%s,1,%s,1_' % (passenger_info['passenger_name'], passenger_info['passenger_id_no']),
            'passengerTicketStr':'%s,0,1,%s,1,%s,%s,N' % (seatType,passenger_info['passenger_name'], passenger_info['passenger_id_no'], passenger_info['mobile_no']),
            'randCode':'',
            'REPEAT_SUBMIT_TOKEN':token,
            'tour_flag':'dc',
            'whatsSelect':'1',
        }
        try:
            resp = self.session.post(url, headers=self.header2, cookies=cookie, data=data)
            resp.raise_for_status
            cookie = resp.cookies.get_dict()
            jsn = resp.json()
            if jsn['status'] is True:
                print('检查命令详情通过！\n')
                if 'tk' in cookie:
                    return cookie['tk']
            else:
                print('__checkOrderInfo出现一些问题！')
                print(jsn, '\n')
                return False
        except Exception as e:
            print('__checkOrderInfo出现错误：%s' % e)
            print(jsn, '\n')
            return False


    def getQueueCount(self, seatType, train_num, train_info, token, cookie):  # trian_info是一个包含火车信息的字典{1：2, ...}
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           current_captcha_type, JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route, tk。
        '''

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        data = {
            '_json_att':'',
            'fromStationTelecode':train_info['fromstation'],
            'leftTicket':train_info['leftTicket'],
            'purpose_codes':'00',
            'REPEAT_SUBMIT_TOKEN':token,
            'seatType':seatType,
            'stationTrainCode':train_num,
            'toStationTelecode':train_info['tostation'],
            'train_date':datetime.strptime(self.date, '%Y-%m-%d').strftime('%a+%b+%d+%Y+00:00:00+GMT+0800'),
            'train_location':train_info['train_location'],
            'train_no':train_info['train_num'],
        }
        try:
            resp = self.session.post(url, headers=self.header2, data=data, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] is True:
                print('获取列队内容成功！\n')
                return True
            else:
                print('__getQueueCount出现错误！')
                print(jsn, '\n')
                return False
        except Exception as e:
            print('__getQueueCount获取列队内容出错：%s' % e)
            print(jsn, '\n')
            return False


    def confirmSingleForQueue(self,passenger_info, train_info, seatType, token, key_check_isChange, cookie):
        '''参数key_check_isChange全部由0-9，A-F组成，应该是一组十六进制字符串。
           请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           current_captcha_type, JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route, tk
           passenger_info:字典。
        '''

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data = {
            '_json_att':'',
            'choose_seats':'',
            'dwAll':'N',
            'Key_check_isChange':key_check_isChange,
            'leftTicketStr':train_info['leftTicket'],
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
            resp = self.session.post(url, data=data, headers=self.header2, cookies=cookie)
            resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] == True:
                print('成功确认订单！\n')
                return True
            else:
                print('确认订单时出现一些错误！')
                print(jsn,'\n')
                return False
        except Exception as e:
            print('__confirmSingleForQueue出错：%s' % e)
            print(jsn, '\n')
            return False


    def queryOrderWaitTime(self,token,cookie):  # 该方法需要循环访问，直至waitTime=-1，waitCount=0,orderld!='null'为止
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           current_captcha_type, JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route, tk。
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
                resp = self.session.get(url, headers=self.header2, params=payload, cookies=cookie)
                resp.raise_for_status
                jsn = resp.json()
                print('请等待...')
                
                if jsn['data']['waitTime'] == -1:
                    return jsn['data']['orderId']
                else:
                    print(jsn, '\n')
        except Exception as e:
            print('__queryOrderWaitTime出错未能完成订票：%s' % e)
            print(jsn, '\n')
            return False


    def result(self, train_num, ord_no, token, train_info, cookie):
        '''请求cookie：_jc_save_fromDate, _jc_save_fromStation, _jc_save_toDate，
           _jc_save_toStation, _jc_save_wfdc_flag:dc, BIGipServerotn, BIGipServerpool_passport, 
           current_captcha_type, JSESSIONID, RAIL_DEVICEID, RAIL_EXPIRATION, route, tk。
        '''
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
        data = {
            '_json_att':'',
            'orderSequence_no':ord_no,
            'REPEAT_SUBMIT_TOKEN':token,
        }
        try:
            resp = self.session.post(url, headers = self.header2, data=data, cookies=cookie)
            # resp.raise_for_status
            jsn = resp.json()
            if jsn['status'] == True:
                print(jsn)
                txt = '您已成功预定了%s至%s的%s，发车时间%s，全程%s。\n请您30分钟内登陆12306进行付款，过期作废。\n'
                print(txt % (self.from_station_cn,self.to_station_cn,train_num,train_info['ctime'],train_info['atime']))
                return True
            else:
                print('订单似乎出现了某些错误...\n')
                return False
        except Exception as e:
            print('确认结果时发现错误：%s' % e)
            print(jsn, '\n')
            return False


    def ticket_check(self, cookie):  # 获取车票信息
        ticket_dict = info_show(self.date, self.from_station, self.to_station, cookie)
        return ticket_dict
