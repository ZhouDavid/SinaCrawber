# -*- coding:utf-8 -*-
import os
import math
import time
import datetime
import random
import re
import json
import sys

import requests
import codecs
import constant

MAX_PAGE=50
begin_time = '2013-2-1 00:00'
end_time = '2016-7-1 23:59'

begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%d %H:%M')
end_time = datetime.datetime.strptime(end_time,'%Y-%m-%d %H:%M')

def showjson(s, count):
    ss = '----'
    sss = '****'
    if not isinstance(s, dict) and not isinstance(s, list):
        print (ss * count, s)
    if isinstance(s, dict):
        for key in s:
            print (sss * count, key)
            showjson(s[key], count + 1)
    if isinstance(s, list):
        for i in s:
            showjson(i, count + 1)


class Spider:
    def updateCookie(self):
        cookie ='SINAGLOBAL=3508472725501.8877.1468079275906; _ga=GA1.2.865931425.1468135266; __gads=ID=b7e4913bae157861:T=1468135260:S=ALNI_MbTsEAM-_WqazyZms5qGARJFWeaEA; wb_bub_hot_5898713520=1; YF-Ugrow-G0=ad06784f6deda07eea88e095402e4243; YF-V5-G0=55f24dd64fe9a2e1eff80675fb41718d; YF-Page-G0=734c07cbfd1a4edf254d8b9173a162eb; _s_tentry=login.sina.com.cn; Apache=6584713805471.305.1468166773532; ULV=1468166773575:3:3:2:6584713805471.305.1468166773532:1468135322333; wb_bub_hot_5894427394=1; WB_register_version=6a140e8e73e40c90; appkey=; wb_bub_hot_5971914513=1; wb_bub_hot_5972341543=1; wb_bub_hot_5972341676=1; WBStore=8ca40a3ef06ad7b2|undefined; UOR=www.google.co.jp,open.weibo.com,login.sina.com.cn; SCF=AoN3i4Zz5zTNqaysPyrmLUGyEL-UDF0iX3Ph5tWj9VXU-a1cCHCwvY4PT9VQG_xvJshqy8p9cZNZMSdxNNIXS98.; SUB=_2A256htfJDeTxGeNH7FAS9C_KzDqIHXVZ8k4BrDV8PUNbmtBeLXDEkW9Fmdx58M11CbRmteD6YRTbT-v2Kg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5Ma6K5_dCbfCI_yYCBuHs15JpX5K2hUgL.Fo-4S0z0Sh2cS0q2dJLoIpMLxKBLB.-LBK5LxK-LB--LBKi2x.xKBBtt; SUHB=0BLYCWjTibpGiE; ALF=1499716376; SSOLoginState=1468180377; un=13717132653; wvr=6; WBtopGlobal_register_version=6a140e8e73e40c90'
        self.cookdic = dict(Cookie=cookie)

    def __init__(self):
        self.updateCookie()
        # self.client = pymongo.MongoClient(constant.MONGODB_HOST, constant.MONGODB_PORT)
        # if (not 'soa' in self.client.database_names() or not 'weibo' in self.client['soa'].collection_names()):
        #     self.client['soa']['weibo'].create_index([('uid', pymongo.ASCENDING)], unique=True)

    def clear_cache(self):
        self.client['soa']['weibo'].remove()

    def get_content(self, toUrl):
        """ Return the content of given url
            Args:
                toUrl: aim url
                count: index of this connect
            Return:
                content if success
                'Fail' if fail
        """
        try:
            req = requests.get(toUrl, verify = False,cookies=self.cookdic, timeout=50)
            time.sleep(1)
        except:
            return None
        if req.status_code != requests.codes.ok:
            print ("haven't get 200, status_code is: " + str(req.status_code));
            return 1
        return req

    def get_weibo(self, inputid):
        # inputUrl = home_page + inputid +'/profile'
        inputUrl = 'http://m.weibo.cn/page/json?containerid=100505' + inputid + '_-_WEIBO_SECOND_PROFILE_WEIBO&page='
        tmpContent = self.get_content(inputUrl + '1')
        s = json.loads(tmpContent.text)
        if 'maxPage' in s['cards'][0]:
            maxPage = s['cards'][0]['maxPage']
        else:
            maxPage = 1
        if maxPage<MAX_PAGE:
            pages=maxPage
        else:
            pages=MAX_PAGE
        print 'maxPage='+str(maxPage)
        my_weibo_list = []
        too_old = False
        delta = math.floor(maxPage/60)
        if delta<1:
            delta = 1
        print 'delta='+str(delta)
        i = 1
        while (i <= maxPage):
            if too_old==True:
                break
            print ("Page %d" % i)
            tmp = self.get_content(inputUrl + str(i))
            if tmp is None:
                i=i+delta
                continue
            if tmp == 1:
                return my_weibo_list
            s = json.loads(tmp.text)

            if 'card_group' not in s['cards'][0]:
                i=i+delta
                continue
            # print s
            # weibo_list = [k['mblog'] for k in s['cards'][0]['card_group']]
            weibo_list = []

            for k in s['cards'][0]['card_group']:
                if 'mblog' in k:
                    weibo_list.append(k['mblog'])
            for weibo in weibo_list:
                my_weibo = {}
                if 'reposts_count' in weibo:
                    my_weibo['reposts_count'] = weibo['reposts_count']
                if 'comments_count' in weibo:
                    my_weibo['comments_count'] = weibo['comments_count']
                if 'like_count' in weibo:
                    my_weibo['like_count'] = weibo['like_count']
                if 'bid' in weibo:
                    my_weibo['bid'] = 'http://weibo.com/' + str(inputid) + '/' + weibo['bid']
                if 'retweeted_status' in weibo:
                    my_weibo['origin'] = '0'
                else:
                    my_weibo['origin'] = '1'
                abored = False
                if 'created_at' in weibo:
                    time = weibo['created_at']
                    tlen = len(time)
                    if tlen==8:
                        time = today+' '+time[3:]
                    elif tlen==11:
                        time = '2016-'+weibo['created_at']
                    elif tlen<8:
                        abored = True
                    if not abored:
                        ttime = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M')
                    else:
                        ttime = datetime.datetime.now()
                    if end_time<ttime:
                        i=i+delta
                        continue
                    elif begin_time>ttime:
                        too_old = True
                        break
                    my_weibo['created_at'] = time
                if 'bmiddle_pic' in weibo or 'original_pic' in weibo or 'thumbnail_pic' in weibo:
                    my_weibo['has_pic'] = '1'
                else:
                    my_weibo['has_pic'] = '0'
                my_weibo_list.append(my_weibo)
            i=i+delta
        return my_weibo_list
    def get_info(self, inputid):
        res=requests.get('https://api.weibo.com/2/users/show.json',
                         params={'source': constant.WEIBO_API_KEY, 'uid': inputid},
                         cookies=self.cookdic,verify=False)
        info_dict = json.loads(res.text)
        # get_weibo(inputid)
        return info_dict

    def get_result(self, inputid):
        return {'uid': inputid, 'updated_at': time.time(), 'weibo_list': self.get_weibo(inputid),
                        'info_dict': self.get_info(inputid),}

    def username_to_uid(self, username):
        print username
        res=requests.get('https://api.weibo.com/2/users/show.json',
                         params={'source': constant.WEIBO_API_KEY, 'screen_name':username},
                         cookies=self.cookdic,verify=False)
        user_text= json.loads(res.text)
        if 'idstr' in user_text:
            user_id = user_text['idstr']
            return user_id
        else:
            print 'user is not found!'
            exit(-1)

    def crawl(self, inputid):
        # 'info_dict':get_info(inputid),
        # cookdic = login.getCookies([{'no':username, 'psw':password}])[0]
        if not constant.CACHE_ENABLE:
            return True, self.get_result(inputid)
        find_row = self.client['soa']['weibo'].find_one({'uid': inputid})
        if (find_row):
            weibo_len = len(find_row['weibo_list'])
            days = (time.time() - find_row['updated_at']) / (60 * 60 * 24)
            if(len <= 50 or days > 14):
                res = self.get_result(inputid)
                self.client['soa']['weibo'].replace_one({'uid':inputid}, res)
                return True, res
            else:
                return False, find_row
        else:
            res = self.get_result(inputid)
            self.client['soa']['weibo'].insert_one(res)
            return True, res

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    print ("Welcome to use this program for crawling data from sina microblo!")
    name_list=['葡萄牙驻华大使馆',\
    '俄罗斯驻华大使馆',\
    '欧盟在中国',\
    '中欧信使',\
    '日本国驻华大使馆',\
    '韩国驻华大使馆',\
    '英国驻华使馆',\
    '法国驻华使馆',\
    '爱尔兰驻华大使馆',\
    '荷兰驻华大使馆',\
    '丹麦驻华大使馆',\
    '澳大利亚驻华使领馆',\
    '委内瑞拉驻华使馆',\
    '瑞典驻华大使馆微博',\
    '奥地利驻华使馆',\
    '印度使馆文化处',\
    '瑞士驻华大使馆',\
    '泰国驻华大使馆',\
    '新西兰驻华大使馆',\
    '以色列驻华使馆',\
    '墨西哥驻华大使馆',\
    '波兰使馆文化处',\
    '意大利驻华使馆',\
    '挪威驻华大使馆',\
    '德国驻华大使馆',\
    '古巴驻华大使馆',\
    '希腊使馆新闻办公室',\
    '秘鲁驻华使馆',\
    '巴西驻华大使馆',\
    '埃及驻华使馆文化处',\
    '印度尼西亚共和国驻广州总领事馆',\
    '保加利亚共和国驻上海总领事馆',\
    '比利时驻华使馆',\
    '哥斯达黎加驻华大使馆',\
    '西班牙驻华大使馆官方微博',\
    '智利驻中国大使馆',\
    '斯里兰卡驻广州总领事馆',\
    '马尔代夫驻华大使馆',\
    ]

    my_spider = Spider()
    user_ids = []
    # for name in name_list:
    #     user_id = my_spider.username_to_uid(name)
    #     user_ids.append(user_id)
    user_ids = ['3802185661', '2503806417', '1974271741', '2912176333', '1938487875', '2394895404', '1663026093',\
                '1987630007', '3854853421', '2511711495', '2001109753', '1918101143', '3247450215' \
                '3260734291', '2861043474','2261322181', '2603537861', '3223655791', '5041530878', '2297867557', '2464455037', '2082506443',\
                '3045655775', '5394927186', '2209621235', \
                '3213889125', '1898996141', '3216802580', '2490644882', '2466916861', '3982986009', '2868342892',\
                '1927332783', '2442073863', '2839805303', '5237350253', '2833027310', '2137856685']
    i = 0
    for id in user_ids:
        print i
        latest,my_weibo_list = my_spider.crawl(id)
        weibo_list = my_weibo_list['weibo_list']
        filename = name_list[i].decode('utf-8').encode('gb2312')
        f = codecs.open(filename,'w','utf-8')
        j = 1
        for weibo in weibo_list:
            record = str(j) + ',' + weibo['created_at'] + ',' + weibo['bid'] + ',' + \
            str(weibo['reposts_count']) + ',' + str(weibo['comments_count']) + ',' + str(weibo['like_count']) + ',' + \
            weibo['origin'] + ',' + weibo['has_pic'] + '\n'
            f.write(record)
            j=j+1
        i=i+1
        f.close()

