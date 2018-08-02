#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen


from simulator import BookingSimulator
from captchaRec import rec_run
from driver import Browser
import time, random


if __name__ == '__main__':
    # username = input('12306账户名：')
    # password = input('12306账户密码：')
    # from_station = input('始发站：')
    # to_station = input('到达站：')
    # date = input('出发日期：')
    username = 'kkchen@msn.cn'
    password = 'KaiChen880326'
    from_station = '北京'
    to_station = '石家庄'
    date = '2018-07-30'

    simulator = BookingSimulator(username, password, from_station, to_station, date)
    browser = Browser()  # 通过Selenium驱动浏览器获取设备信息
    
    # train_num = input('选择的车次：')  
    # # seatType = input('选择的座位类型（特等商务：9，一等：M，二等：O，软卧：4，硬卧：3，软座：2，硬座：1）：') 
    # seatType = 'O'
    
    print('与服务器创建会话...\n')
    browser.init()
    browser.ticket_check(from_station, to_station)
    cookie = browser.get_cookie()
    BIGipServerotn = cookie['BIGipServerotn']
    jsessionid = cookie['JSESSIONID']
    route = cookie['route']
    dfp = cookie['RAIL_DEVICEID']
    exp = cookie['RAIL_EXPIRATION']
    

    print('查询余票...')
    cookie_for_ticket = {
        '_jc_save_fromDate':simulator._jc_save_fromdate,
        '_jc_save_fromStation':simulator._jc_save_fromstation,
        '_jc_save_toDate':simulator._jc_save_todate,
        '_jc_save_toStation':simulator._jc_save_tostation,
        '_jc_save_wfdc_flag':'dc',
        'BIGipServerotn':BIGipServerotn,
        'JSESSIONID':jsessionid,
        'RAIL_DEVICEID':dfp,
        'RAIL_EXPIRATION':exp,
        'route':route,
    }
    train = simulator.ticket_check(cookie_for_ticket)
    train_num = input('选择车次：')
    seatType = input('选择的座位类型（特等商务：9，一等：M，二等：O，软卧：4，硬卧：3，软座：2，硬座：1）：')
    train_info = train[train_num]

    print('检查登陆状态...')
    cookie_for_user = {
        '_jc_save_fromDate':simulator._jc_save_fromdate,
        '_jc_save_fromStation':simulator._jc_save_fromstation,
        '_jc_save_toDate':simulator._jc_save_todate,
        '_jc_save_toStation':simulator._jc_save_tostation,
        '_jc_save_wfdc_flag':'dc',
        'BIGipServerotn':BIGipServerotn,
        'JSESSIONID':jsessionid,
        'RAIL_DEVICEID':dfp,
        'RAIL_EXPIRATION':exp,
        'route':route,
    }
    simulator.checkUser(cookie_for_user)

    # 识别验证码失败反复获取识别
    while True:
        print('正在获取验证码...\n')
        # 用于获取验证码的cookie
        cookie_2 = {
            '_jc_save_fromDate':simulator._jc_save_fromdate,
            '_jc_save_fromStation':simulator._jc_save_fromstation,
            '_jc_save_toDate':simulator._jc_save_todate,
            '_jc_save_toStation':simulator._jc_save_tostation,
            '_jc_save_wfdc_flag':'dc',
            'BIGipServerotn':BIGipServerotn,
            'RAIL_DEVICEID':dfp,
            'RAIL_EXPIRATION':exp,
            'route':route,
        }
        im, cookie = simulator.captcha_image(cookie_2)
        BIGipServerpool_passport = cookie['BIGipServerpool_passport']
        _passport_ct = cookie['_passport_ct']
        _passport_session = cookie['_passport_session']

        print('识别验证码...\n')
        answer = rec_run(im)

        print('发送识别结果...\n')
        # 用于验证码校验的cookie
        cookie_3 = {
            '_jc_save_fromDate':simulator._jc_save_fromdate,
            '_jc_save_fromStation':simulator._jc_save_fromstation,
            '_jc_save_toDate':simulator._jc_save_todate,
            '_jc_save_toStation':simulator._jc_save_tostation,
            '_jc_save_wfdc_flag':'dc',
            '_passport_ct':_passport_ct,
            '_passport_session':_passport_session,
            'BIGipServerotn':BIGipServerotn,
            'BIGipServerpool_passport':BIGipServerpool_passport,
            'RAIL_DEVICEID':dfp,
            'RAIL_EXPIRATION':exp,
            'route':route,
        }
        if simulator.captcha_check(answer, cookie_3):
            break
    
    print('用户登陆...\n')
    # 用于用户登陆的cookie
    cookie_4 = cookie_3
    uamtk = simulator.login(cookie_4)

    print('获取tk...\n')
    # 用于uamtk的cookie
    cookie_5 = {
        '_jc_save_fromDate':simulator._jc_save_fromdate,
        '_jc_save_fromStation':simulator._jc_save_fromstation,
        '_jc_save_toDate':simulator._jc_save_todate,
        '_jc_save_toStation':simulator._jc_save_tostation,
        '_jc_save_wfdc_flag':'dc',
        '_passport_session':_passport_session,
        'BIGipServerotn':BIGipServerotn,
        'BIGipServerpool_passport':BIGipServerpool_passport,
        'RAIL_DEVICEID':dfp,
        'RAIL_EXPIRATION':exp,
        'route':route,
        'uamtk':uamtk,
    }
    tk = simulator.uamtk(cookie_5)

    print('发送tk到服务器...\n')
    # 用于uamauthclient的cookie
    cookie_6 = {
        '_jc_save_fromDate':simulator._jc_save_fromdate,
        '_jc_save_fromStation':simulator._jc_save_fromstation,
        '_jc_save_toDate':simulator._jc_save_todate,
        '_jc_save_toStation':simulator._jc_save_tostation,
        '_jc_save_wfdc_flag':'dc',
        'BIGipServerotn':BIGipServerotn,
        'BIGipServerpool_passport':BIGipServerpool_passport,
        'JSESSIONID':jsessionid,
        'RAIL_DEVICEID':dfp,
        'RAIL_EXPIRATION':exp,
        'route':route,
    }
    simulator.uamauthclient(cookie_6, tk)
    print('登陆成功！\n')


    print('提交命令请求...\n')
    # 用于提交命令的cookie
    cookie_7 = {
        '_jc_save_fromDate':simulator._jc_save_fromdate,
        '_jc_save_fromStation':simulator._jc_save_fromstation,
        '_jc_save_toDate':simulator._jc_save_todate,
        '_jc_save_toStation':simulator._jc_save_tostation,
        '_jc_save_wfdc_flag':'dc',
        'BIGipServerotn':BIGipServerotn,
        'BIGipServerpool_passport':BIGipServerpool_passport,
        'JSESSIONID':jsessionid,
        'RAIL_DEVICEID':dfp,
        'RAIL_EXPIRATION':exp,
        'route':route,
        'tk':tk
    }
    simulator.submitOrderRequest(train_info, cookie_7)
    
    print('获取token...\n')
    # 用于获取token的cookie
    cookie_8 = cookie_7
    token, key_check_isChange = simulator.initDc(cookie_8)
    

    print('获取账户中的乘客信息...\n')
    # 获取乘客信息的cookie
    cookie_9 = cookie_8
    dtos = simulator.getPassengerDTOs(cookie_9, token)
    for p in dtos:
        print(p['passenger_name'], end='\t')
    # p_n = input('请输入乘客名称：')
    p_n = '陈凯'
    for p in dtos:
        if p['passenger_name'] == p_n:
            passenger_info = p
    
    print('获取当前验证码类型...\n')
    cookie_10 = cookie_9
    current_captcha_type = simulator.getPassCodeNew(cookie_9)
    time.sleep(random.random()*3)

    print('检查命令详情...\n')
    # 用于checkorderinfo的cookie
    cookie_11 = {
        '_jc_save_fromDate':simulator._jc_save_fromdate,
        '_jc_save_fromStation':simulator._jc_save_fromstation,
        '_jc_save_toDate':simulator._jc_save_todate,
        '_jc_save_toStation':simulator._jc_save_tostation,
        '_jc_save_wfdc_flag':'dc',
        'BIGipServerotn':BIGipServerotn,
        'BIGipServerpool_passport':BIGipServerpool_passport,
        'current_captcha_type':current_captcha_type,
        'JSESSIONID':jsessionid,
        'RAIL_DEVICEID':dfp,
        'RAIL_EXPIRATION':exp,
        'route':route,
        'tk':tk
    }
    new_tk = simulator.checkOrderInfo(seatType, cookie_11, passenger_info, token)
    if new_tk:
        print('new_tk=%s' % new_tk)
        cookie_11.update({'tk':new_tk})
    
    print('__getQueueCount 获取列队内容...\n')
    # cookie 与上部相同
    simulator.getQueueCount(seatType, train_num, train_info, token, cookie_11)

    print('确认信息列队...\n')
    # cookie与上部相同
    simulator.confirmSingleForQueue( passenger_info, train_info, seatType, token, key_check_isChange, cookie_11)
    
    print('确认订票信息...\n')
    # cookie与上步相同
    ord_no = simulator.queryOrderWaitTime(token, cookie_11)
    simulator.result(train_num, ord_no, token, train_info, cookie_11)
    
