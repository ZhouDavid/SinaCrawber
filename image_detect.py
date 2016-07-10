__author__ = 'Nyunyunyunyu'

from pprint import pformat
import os

import requests
import pymongo

from facepp import API, File
import constant


def print_result(hint, result):
    def encode(obj):
        if type(obj) is unicode:
            return obj.encode('utf-8')
        if type(obj) is dict:
            return {encode(k): encode(v) for (k, v) in obj.iteritems()}
        if type(obj) is list:
            return [encode(i) for i in obj]
        return obj
    print (hint)
    result = encode(result)
    print ('\n'.join(['  ' + i for i in pformat(result, width = 75).split('\n')]))

def get_filename(url):
    return url.split('/')[-1]

def weibo_image_extract(weibo):
    image_url_list = []
    for weibo in weibo['weibo_list']:
        if weibo.has_key('pics'):
            for img in weibo['pics']:
                image_url_list.append(img['bmiddle_pic'])
    return image_url_list

def download_all_weibo_image(uid, image_url_list):
    image_cache_path = os.path.join(constant.IMAGE_CACHE_DIR, uid)
    if not os.path.exists(constant.IMAGE_CACHE_DIR):
        os.mkdir(constant.IMAGE_CACHE_DIR)
    if not os.path.exists(image_cache_path):
        os.mkdir(image_cache_path)
    for url in image_url_list:
        file_name = os.path.join(image_cache_path, get_filename(url)).encode('utf-8')
        if os.path.exists(file_name):
            if os.path.isdir(file_name):
                raise Exception('Exist directory with the same name')
            else:
                continue
        fout = open(file_name, 'w')
        req = requests.get(url)
        fout.write(req.content)
        fout.close()

def face_image_detect(uid, image_url_list):
    image_cache_path = os.path.join(constant.IMAGE_CACHE_DIR, uid)
    face_image_url = {}
    api = API(constant.FACEPP_API_KEY, constant.FACEPP_API_SECRET)
    for url in image_url_list:
        # print url
        file_name = os.path.join(image_cache_path, get_filename(url)).encode('utf-8')
        img = File(file_name)
        rst = api.detection.detect(img=img)
        if len(rst['face']):
            face_image_url[url] = rst
    return face_image_url

def face_grouping(uid, face_image_url):
    api = API(constant.FACEPP_API_KEY, constant.FACEPP_API_SECRET)
    rst = api.faceset.create()
    faceset_id = rst['faceset_id']
    for url in face_image_url:
        for face in face_image_url[url]['face']:
            res = api.faceset.add_face(faceset_id=faceset_id, face_id = face['face_id'])
    session_id = api.grouping.grouping(faceset_id = faceset_id)
    session_id = session_id['session_id']
    rst = api.wait_async(session_id)
    api.faceset.delete(faceset_id=faceset_id)
    if not rst.has_key('result'):
        raise Exception('API return error')
    return rst['result']

def get_grouping_result_online(weibo):
    image_url_list = weibo_image_extract(weibo)
    uid = weibo['uid']
    download_all_weibo_image(uid, image_url_list)
    face_image_url = face_image_detect(uid, image_url_list)
    grouping_rst = face_grouping(uid, face_image_url)
    ans = []
    for group in grouping_rst['group']:
        tmp = []
        for face in group:
            tmp.append(face['face_id'])
        ans.append(tmp)
    face_info_dict = {}
    for url in face_image_url:
        for face_info in face_image_url[url]['face']:
            face_info['url'] = url
            face_id = face_info['face_id']
            face_info_dict[face_id] = face_info
    return ans, face_info_dict

def get_grouping_result(weibo, need_update):
    client = pymongo.MongoClient(constant.MONGODB_HOST, constant.MONGODB_PORT)
    if (not 'soa' in client.database_names() or not 'image_grouping' in client['soa'].collection_names()):
        client['soa']['image_grouping'].create_index([('uid', pymongo.ASCENDING)], unique=True)
    if not constant.CACHE_ENABLE:
        return get_grouping_result_online(weibo)
    uid = weibo['uid']
    find_row = client['soa']['image_grouping'].find_one({'uid': uid})
    if (find_row):
        if(need_update):
            res = get_grouping_result_online(weibo)
            client['soa']['image_grouping'].replace_one({'uid':uid}, {'uid':uid, 'grouping_info':res})
            return res
        else:
            return find_row['grouping_info']
    else:
        res = get_grouping_result_online(weibo)
        client['soa']['image_grouping'].insert_one({'uid':uid, 'grouping_info':res})
        return res

if __name__ == "__main__":
    pass
    # IMAGE_DIR = 'http://cn.faceplusplus.com/static/resources/python_demo/'
    # PERSONS = [ IMAGE_DIR + '1.jpg', IMAGE_DIR + '2.jpg', IMAGE_DIR + '3.jpg',
    #             'https://ss0.bdstatic.com/94oJfD_bAAcT8t7mm9GUKT-xh_/timg?image&quality=100&size=b4000_4000&sec=1464359897&di=7949bfdb20c2f627de63b5924cc8fd13&src=http://jiangsu.china.com.cn/uploadfile/2013/0327/20130327085601230.jpg']
    # res = face_image_detect(PERSONS)
    # print_result('aa',res)
