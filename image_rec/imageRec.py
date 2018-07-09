# !/usr/bin/env python
# -*- coding: utf-8 -*-

from .tokens.get_tokens import get_token
import requests, base64, json

def recognize(image, access_token, flag):
    '''
       返回图片识别结果的字典。
       参数解析：
       -image:str,图片的绝对路径。
       -access_token:str,需要根据百度AI开放平台提供的API Key和Secret Key得到。
                     可以使用tokens中get_token.py中的get_token()方法。
       -flag: type, content or position. type时为识别主题类型，content为识别内容，position识别主题位置。

        返回结果的键解释：
        log_id: int,每个结果唯一的id，
        result_num: int,返回结果的数据，即result中元素个数，
        resul: list,返回结果字典的列表，
        +score: float or int, 结果的置信度，范围再0-1，
        +root：识别结果的分类，上层标签，
        +keyword：图片中物体或场景名。
    '''
    base_url_t = 'https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general'
    base_url_c = 'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic'
    base_url_p = 'https://aip.baidubce.com/rest/2.0/image-classify/v1/object_detect'
    payload = {
        'access_token':access_token,
    }
    header = {
        'Content-Type':'application/x-www.form-urlencoded',
    }
    with open(image, 'br') as f:
        obj = base64.b64encode(f.read())
    if flag == 'content':
        resp = requests.post(url=base_url_c, params=payload, headers=header, data={'image':obj})
    elif flag == 'type':
        resp = requests.post(url=base_url_t, params=payload, headers=header, data={'image':obj})
    elif flag == 'position':
        resp = requests.post(url=base_url_p, params=payload, headers=header, data={'image':obj})
    resp.encoding = resp.apparent_encoding
    dic = resp.json()
    return dic

if __name__ == '__main__':
    ak = input('输入你的API Key：')
    sk = input('输入你的Secret Key：')
    file = input('需要识别的图片路径：')
    flag = input('识别类型（type：主题类型，content：内容，position：主体位置）：')
    access_token = get_token(ak=ak,sk=sk, flag=flag)['access_token']
    dic = recognize(r'%s' % file, access_token, flag=flag)
    print(dic)
    input('按任意键退出！')
