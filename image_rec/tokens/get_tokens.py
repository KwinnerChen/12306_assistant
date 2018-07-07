# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import json
import time

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'access_token_%s.jsn')

def _refresh_token(ak, sk):  # 请求token，返回字典
    '''ak:API_Key,
       sk:Secret_Key,
    '''
    base_url = 'https://aip.baidubce.com/oauth/2.0/token'
    payload = {
        'grant_type':'client_credentials',
        'client_id':ak,
        'client_secret':sk,
    }
    header = {
        'Content-Type':'application/json; charset=UTF-8',
    }
    resp = requests.post(url=base_url, params=payload, headers=header)
    dic = resp.json()
    dic.update({'client_id':ak, 'client_secret':sk})
    return dic

def get_token(ak, sk, flag):  # 试图从文件读取token，过期或不存在或密钥不匹配刷新后，再返回字典
    '''用于获取ak=api_key,sk=secret_key,type=content|position|type的token，返回的是一个字典。ak,sk在百度开放AI平台账户生成。
       用于检测类型时为type，用于检测内容时为content,主体位置时为position。
       结果字典类似包含:
       "refresh_token":str,
       "expires_in":int，有效时间，秒，
       "scope":str,
       "session_key":str,
       "access_token:str,用于api,
       "session_secret":str
       '''
    
    if os.path.isfile(file_path%flag) and os.path.getsize(file_path%flag)>0:
        with open(file_path%flag, '+r') as f:
            dic = json.load(f)
            if dic['client_id'] != ak or dic['client_secret'] != sk:
                dic = _refresh_token(ak, sk)
                json.dump(dic, f)
                return dic
            elif time.time()-os.path.getatime(file_path%flag) > dic.get('expires_in'):
                dic = _refresh_token(ak, sk)
                json.dump(dic, f)
                return dic         
            else:
                return dic
    else:
        dic = _refresh_token(ak, sk)
        with open(file_path%flag, 'w') as f:
            json.dump(dic, f)
        return dic

if __name__ == '__main__':
    ak = input('输入API Key：')
    sk = input('输入Secret Key:')
    flag = input('要识别的类型（type|content|position):')
    dic = get_token(ak=ak, sk=sk, flag=flag)
    print('你的access_token是：%s' % dic['access_token'])
    input('任意键退出！')