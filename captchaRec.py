#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen


from lxml import etree
from base64 import b64decode
import requests
import random
import os
import _io


'''提供了在线的对12306验证码的解析，返回的是一个符合12306post参数标准的字符串'''

str_b = b64decode(b'aHR0cDovL2xpdHRsZWJpZ2x1by5xaWNwLm5ldDo0NzcyMC8=')
url = str_b.decode('utf-8')

def __rec(im_path): 
    '''接受一个图片路径或者一个以二进制打开的文件句柄或者一个bytes对象'''
    
    if isinstance(im_path, str):
        if os.path.isfile(im_path):
            with open(im_path, 'rb') as f:
                file = {'file':f}
                resp = requests.post(url, files=file)
                resp.raise_for_status
                html = resp.text
                return html
        else:
            raise TypeError('''接受一个图片路径或者一个以二进制打开的文件句柄或者一个二进制字符串''')
    elif isinstance(im_path, _io._BufferedIOBase):
        file = {'file':im_path}
        resp = requests.post(url, files=file)
        resp.raise_for_status
        html = resp.text
        return html
    elif isinstance(im_path, bytes):
        file = {'file':('captcha-image.jpg',im_path)}
        resp = requests.post(url, files=file)
        resp.raise_for_status
        html = resp.text
        return html
    else:
        raise TypeError('''接受一个图片路径或者一个以二进制打开的文件句柄或者一个二进制字符串。''')


def __page_parser(page):
    tree = etree.HTML(page)
    string = tree.xpath('//b/text()')[0]
    result = tuple(string.split(' '))
    return result


def __rec_parser(result):
    a = (40 + random.choice((-1,1))*random.randint(1,5), 40 + random.choice((-1,1))*random.randint(1,5))
    b = (110 + random.choice((-1,1))*random.randint(1,5), 40 + random.choice((-1,1))*random.randint(1,5))
    c = (180 + random.choice((-1,1))*random.randint(1,5), 40 + random.choice((-1,1))*random.randint(1,5))
    d = (250 + random.choice((-1,1))*random.randint(1,5), 40 + random.choice((-1,1))*random.randint(1,5))
    e = (40 + random.choice((-1,1))*random.randint(1,5), 110 + random.choice((-1,1))*random.randint(1,5))
    f = (110 + random.choice((-1,1))*random.randint(1,5), 110 + random.choice((-1,1))*random.randint(1,5))
    g = (180 + random.choice((-1,1))*random.randint(1,5), 110 + random.choice((-1,1))*random.randint(1,5))
    h = (250 + random.choice((-1,1))*random.randint(1,5), 110 + random.choice((-1,1))*random.randint(1,5))
    answer = list()
    for i in result:
        if i is '1':
            answer.extend(a)
        elif i is '2':
            answer.extend(b)
        elif i is '3':
            answer.extend(c)
        elif i is '4':
            answer.extend(d)
        elif i is '5':
            answer.extend(e)
        elif i is '6':
            answer.extend(f)
        elif i is '7':
            answer.extend(g)
        elif i is '8':
            answer.extend(h)
    return ','.join(map(str,answer))


def rec_run(im_path):
    '''接受一个图片路径或者一个以二进制打开的文件句柄或者一个二进制字符串'''
    page = __rec(im_path)
    result = __page_parser(page)
    answer = __rec_parser(result)
    return answer


if __name__ == '__main__':
    while True:
        temp = input('输入要识别的图片（可以是路径，打开的文件句柄，或者图片的byte对象，q退出。）：')
        if temp == 'q':
            break
        r = rec_run(temp)
        print(r)
