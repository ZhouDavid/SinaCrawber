# -*- coding: utf-8 -*-
# @Author: fibears
# @Date:   2016-05-05 15:21:59
# @Last Modified by:   fibears
# @Last Modified time: 2016-05-09 13:47:40

import json
import random

import requests

from agents import AGENTS


def getCookies(weibo):
    """ 获取Cookies """
    cookies = []
    loginURL = 'https://passport.weibo.cn/sso/login'
    for element in weibo:
        username = element['no']
        password = element['psw']
        postData = {
            "username": username,
            "password": password,
        }
        headers = {
            'User-Agent': random.choice(AGENTS),
            'Host': 'passport.weibo.cn',
            'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F'
        }
        session = requests.Session()
        r = session.post(loginURL, data=postData, headers=headers)
        jsonStr = r.content.decode('utf-8')
        info = json.loads(jsonStr)
        cookie = session.cookies.get_dict()
        if len(cookie) != 0:
            print "Get Cookie Success!( Account:%s )" % username
            cookies.append(cookie)
        else:
            print "Failed!"
            raise Exception("Failed to get Cookie.")
    return cookies
