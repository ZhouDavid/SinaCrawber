# -*- coding:utf-8 -*-
import time
import datetime
import re
import json
import sys

import requests
#import certifi
#from bs4 import BeautifulSoup
#import pymongo
import codecs
#import image_detect
import constant

MAX_PAGE=100
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
        cookie ='SINAGLOBAL=1235433884430.6768.1430467351374; _s_tentry=www.24en.com; Apache=8935136484119.293.1467168964042; ULV=1467168964055:28:4:1:8935136484119.293.1467168964042:1466730010352; YF-Ugrow-G0=ea90f703b7694b74b62d38420b5273df; YF-V5-G0=d22a701aae075ca04c11f0ef68835839; YF-Page-G0=d52660735d1ea4ed313e0beb68c05fc5; WBtopGlobal_register_version=c5a1a241471e96ea; WBStore=8ca40a3ef06ad7b2|undefined; wb_bub_hot_2243006675=1; UOR=,,login.sina.com.cn; SCF=AiC3Rgm6u3z9xSgKzd--JNljSASLf43Sagws6VbO68B_Njg4lQKwyKuw0wHBiCyAKRtYXZ4G0oBsf4YaLF6qW5s.; SUB=_2A256hMcqDeTxGeNG4lYV8inPwjiIHXVZ87_irDV8PUNbmtBeLVbFkW-KQ7Wl7zTYxeYPLyMs3-kSddebmA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFSmMZEdn1kmBrdvnWgNJZF5JpX5K2hUgL.Fo-R1KBXeoM01KB2dJLoI7y.IgUDUsvfU5tt; SUHB=0nl-BuZEgkeyp-; ALF=1499589370; SSOLoginState=1468053370; un=soadigitout@itispxm.com; wvr=6; wb_bub_hot_5894427394=1'
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
        # f = file('weibo.txt','w')
        # f.write(str(s))
        # f.close()
        # print a.keys()
        # showjson(s, 0)
        if 'maxPage' in s['cards'][0]:
            maxPage = s['cards'][0]['maxPage']
        else:
            maxPage = 1
        my_weibo_list = []
        for i in xrange(1, MAX_PAGE + 1):
            print ("Page %d" % i)
            tmp = self.get_content(inputUrl + str(i))
            if tmp is None:
                continue
            if tmp == 1:
                return my_weibo_list
            s = json.loads(tmp.text)

            if 'card_group' not in s['cards'][0]:
                continue
            # print s
            # weibo_list = [k['mblog'] for k in s['cards'][0]['card_group']]
            weibo_list = []

            for k in s['cards'][0]['card_group']:
                if 'mblog' in k:
                    weibo_list.append(k['mblog'])
            for weibo in weibo_list:
                my_weibo = {}
                # showjson(weibo, 0)
                if 'created_at' in weibo:
                	time = weibo['created_at']
              		if not time[0]=='2'and not time[1]=='0':
              			time = '2016-'+weibo['created_at']
              		ttime=datetime.datetime.strptime(time,'%Y-%m-%d %H:%M')
              		if begin_time>ttime:
              			break
              		elif end_time<ttime:
              			continue
              		else:
              			my_weibo['created_at'] = time
                # text
                # if 'text' in weibo:
                #     my_weibo['text'] = weibo['text']
                # # mobile phone
                # if 'source' in weibo:
                #     my_weibo['source'] = weibo['source']
                # if 'url_struct' in weibo:
                #     if weibo['url_struct'][0]['url_type'] == 36:
                #         # showjson(weibo['url_struct'],0)
                #         # print weibo['url_struct'][0]['short_url']
                #         content = self.get_content(weibo['url_struct'][0]['short_url'])
                #         if content:
                #             short_url_data = content.text
                #             pattern = u'location.replace\("([^"]*)"\)'
                #             url_data = short_url_data
                #             # 地址数据
                #             pattern = u'poiid=([^\&]*)\&amp'
                #             mm = re.search(pattern, url_data)
                #             if mm:
                #                 # print mm.group(1)
                #                     # print mm.group(1)
                #                 # print url_data
                #                 my_weibo['location_name'] = weibo['url_struct'][0]['url_title']
                #                 [lon,lat] = mm.group(1).split('_')
                #                 my_weibo['location_lon'] = lon
                #                 my_weibo['location_lat'] = lat
                #                 # print my_weibo['location']
                #                 # <src="http://place.weibo.com/index.php?_p=place_page&amp;_a=poi_map_right&amp;poiid=1013247614"
                #                 # poiObject.lon = 116.307620521;
                #                 # poiObject.lat = 39.9841806635;
                #             else:
                #                 # print 'checkin'
                #                 # print url_data
                #                 pattern = u'poiid=([^\']*)\''
                #                 mmm = re.search(pattern, url_data)
                #                 if mmm:
                #                     # print mmm.group(1)
                #                     placeid = mmm.group(1)
                #                     url = "http://place.weibo.com/index.php?_p=place_page&_a=poi_map_right&poiid="+placeid
                #                     # newcookiedic = login.getCookies([{'no':username, 'psw':password}])[0]
                #                     content = self.get_content(url)
                #                     if content:
                #                         # print '*'*100
                #                         # print content.text
                #                         p1 = u'poiObject.lon = ([^;]*);'
                #                         m1 = re.search(p1, content.text)
                #                         p2 = u'poiObject.lat = ([^;]*);'
                #                         m2 = re.search(p2, content.text)
                #                         if m1 and m2:
                #                             lon = m1.group(1)
                #                             lat = m2.group(1)
                #                             my_weibo['location_name'] = weibo['url_struct'][0]['url_title']
                #                             my_weibo['location_lon'] = lon
                #                             my_weibo['location_lat'] = lat

                if 'reposts_count' in weibo:#转发量
                	my_weibo['reposts_count'] = weibo['reposts_count']

                if 'comments_count' in weibo:#评论数
                	my_weibo['comments_count'] = weibo['comments_count']

                if 'like_count' in weibo:#点赞量
                	my_weibo['like_count'] = weibo['like_count']

                if 'retweeted_status' in weibo:#是否原创
                	my_weibo['origin'] = '0'
                else:
                	my_weibo['origin'] = '1'

                if 'bmiddle_pic' in weibo or 'original_pic' in weibo or 'thumbnail_pic' in weibo:
                	my_weibo['has_pic'] = '1'
                else:
                	my_weibo['has_pic'] = '0'

                if 'bid' in weibo:
                	my_weibo['bid'] = 'http://weibo.com/'+str(inputid)+'/'+weibo['bid']
                thumbnail_url = 'http://ww1.sinaimg.cn/thumbnail/'
                bmiddle_url = 'http://ww1.sinaimg.cn/bmiddle/'
                original_url = 'http://ww1.sinaimg.cn/large/'
                # if 'pics' in weibo:
                #     pics_list = []
                #     for pic in weibo['pics']:
                #         pics_list.append({'thumbnail_pic':thumbnail_url+pic['pid'], 'bmiddle_pic':bmiddle_url+pic['pid'], 'original_pic':original_url+pic['pid']})
                #     my_weibo['pics'] = pics_list
                # if 'thumbnail_pic' in weibo:
                #     my_weibo['thumbnail_pic'] = weibo['thumbnail_pic']
                # if 'bmiddle_pic' in weibo:
                #     my_weibo['bmiddle_pic'] = weibo['bmiddle_pic']
                # if 'original_pic' in weibo:
                #     my_weibo['original_pic'] = weibo['original_pic']
                my_weibo_list.append(my_weibo)

        # showjson(my_weibo_list, 0)
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
    	username = username.decode('gb2312').encode('utf-8')#将输入的中文字符转换为utf8编码
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
	info = '请输入微博用户名:'
	info = info.encode('gb2312')
	print ("Welcome to use this program for crawling data from sina microblo!")
	username = raw_input(info)
	#file = open(filename,'r')
	#usernames =[]

	# while 1:
	# 	name = file.readline()
	# 	if not name:
	# 		break
	# 	usernames.append(name)
	# 	pass

	my_spider = Spider()
	user_id = my_spider.username_to_uid(username)
	latest, my_weibo_list = my_spider.crawl(user_id)
	weibo_list = my_weibo_list['weibo_list']
	f = codecs.open(username,'w','utf-8')
	i=1
	for weibo in weibo_list:
		record = str(i)+','+weibo['created_at']+','+weibo['bid']+','+str(weibo['reposts_count'])+','+str(weibo['comments_count'])+','+str(weibo['like_count'])+','+weibo['origin']+','+weibo['has_pic']+'\n'  
		f.write(record)
		i=i+1
	#print my_weibo_list['weibo_list'][2]['has_pic']
	f.close()
	# my_spider.clear_cache()
	# for username in usernames:
	# 	print ("Getting Weibo...")
	# 	user_id = my_spider.username_to_uid(username)
	# 	latest, my_weibo_list = my_spider.crawl('1631851494')
	# 	weibo_list = my_weibo_list['weibo_list']
	# 	#写入文件
	# 	i=1
	# 	f = codecs.open('美国驻华大使馆','w','utf-8')
	# 	for weibo in weibo_list:
	# 		record = str(i)+','+weibo['created_at']+','+weibo['bid']+','+str(weibo['reposts_count'])+','+str(weibo['comments_count'])+','+str(weibo['like_count'])+','+str(weibo['origin'])+','+str(weibo['has_pic'])+'\n'  
	# 		f.write(record)
	# 		i=i+1
	# 		#print my_weibo_list['weibo_list'][2]['has_pic']
	# 	f.close()
	
	# thanks = '不用谢我，我是活雷锋~'
	# thanks = thanks.encode('gb2312')
	# print (thanks)
    # def get_result(self, inputid):
    #     return {'uid': inputid, 'updated_at': time.time(), 'weibo_list': self.get_weibo(inputid),
    #                     'info_dict': self.get_info(inputid),}
