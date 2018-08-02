#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen

import requests 
import json 
import os
import time


class StationMap(dict, object):

    '''
       对象提供了类似python字典功能。当获取一个车站名时，首先试图由对象本身获取，如果不存在则优先加载本地文件再返回，
       若本地文件也不存在，则从网络获取，解析后返回目标值，并存储到本地已被后用。本地地图有效期为3个月，过期自动更新。
       >>> map_dic = StationMap()  # 也可使用类方法get_dict()来获取对象StationMap.get_dict()
       >>> map_dic['北京'] = 'BJP'
    '''

    def __init__(self):
        super().__init__()
        self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'station_map.json')
        try:
            self.__load_dict()
        except Exception:
            print('由于地图不存在或本地地图已超时，现在更新新本地地图...')
            string=self.__refresh_map()
            self.__string_paser(string)
            self.__storage_map()


    @classmethod
    def get_dict(cls):
        '''该方法返回一个对象本身的实例'''

        return cls()

    def __load_dict(self):  # 由本地文件加载到对象本身
        if time.time() - os.path.getmtime(self.file_path) < 7776000:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                dic = json.load(f)
                self.update(dic)
                return self
        else:
            raise TimeoutError


    def __refresh_map(self):  # 从网络获取地图字符串
        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9056'
        header = {'User-Agent':'Mozilla/5.0'}
        try:
            resp = requests.get(url, headers=header)
            resp.raise_for_status
            string = resp.text
            return string
        except requests.HTTPError as e:
            print('跟新车站地图时出错：%s!' % e)


    def __string_paser(self, string):  # 解析字典字符串，并加载到对象本身
        for i in string.split('@')[1:]:
            l_i = i.split('|')
            self[l_i[1]] = l_i[2]
        return self


    def __storage_map(self):  # 将对象本身存储到本地，已被后用
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self, f)

    # def __getitem__(self, n):  # 获取目标key，已加载的且存在返回，否则加载本地文件，文件不存在更新
    #     r = self.get(n)
    #     if r:
    #         return r
    #     else:
    #         if os.path.exists(self.file_path) and os.path.isfile(self.file_path) and os.path.getsize(self.file_path) > 0:
    #             self.__load_dict()    
    #             return self.get(n)
    #         else:
    #             string = self.__refresh_map()
    #             self.__string_paser(string)
    #             self.__storage_map()
    #             return self.get(n)
