#coding:utf8
from faker import Factory
import requests
import json
import time
import re
import os
import sys
from bs4 import BeautifulSoup
from gevent.pool import Pool
from gevent.queue import Queue
from gevent import monkey
import io
import gevent
import linecache
import chardet
from urllib.parse import unquote,unquote_to_bytes
fake = Factory.create('zh_CN')    

origin_headers = {
    # 'Accept':'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
    # 'Origin':'https://login.xiami.com',
    # 'X-Requested-With':'XMLHttpRequest',
    'User-Agent':fake.user_agent(),
    'Referer':'https://login.xiami.com/member/login',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.8',
}

def get_login_session(email,password):
    config={
        'done': '/',
        'email':email,
        'password':password,
        'submit':'登 录',
        'from':'web',
    }
    s = requests.Session()
    s.headers=origin_headers
    resp = s.post('http://www.xiami.com/member/login', data=config, headers=origin_headers)
    result_json = resp.json()
    print(resp.text)
    if result_json['status'] != True:
        print('fail')
    else:
        result_data = result_json['data']
        user_id,nick_name = result_data.get('user_id'),result_data.get('nick_name')
    return s,user_id

def get_response(url,s):
    return s.get(url)

class Tags(object):
    """docstring for Tags"""
    def __init__(self):
        super(Tags, self).__init__()
        album = 'lib-song'
        self._s,self._id = get_login_session(email,password)
        self.album = {'name':album, 'user':self._id}       
        # self._s,self._id = get_login_session(args.email,args.password)
        # self.album = {name:args.album, user:self._id}
        self.base_path = '.cache/'+album+'/'

    def get_song_list(self,url,status='1'):
        page_id = int(url[-1])
        if page_id != 1:
            page_pre = url[:-1]+str(page_id-1)
            print(page_pre)
        else:
            page_pre = url
        print(page_pre)
        self._s.headers.update({
            'Referer':url,
        })
        html_list = self._s.get(url).text
        soup = BeautifulSoup(html_list, 'html.parser')
        tr_list = soup.find_all('tr',attrs={"data-playstatus": status})
        song_list = []
        pattern = r'[\d]+'
        for song in tr_list:
            song_id = re.search(pattern,song['id']).group(0)
            song_list.append(song_id)
        return song_list

    def get_song_url(self,song_id):
        tmp = ''.join(str(time.time()).split('.'))[:13]
        params={
            '_':tmp,
            'type':'song',
            'id': str(song_id),
            'quality':2,
        }
        down_url = 'http://www.xiami.com/download/get-link'
        self._s.headers.update({
            'Referer':'http://www.xiami.com/song/{}'.format(song_id),
            'X-Requested-With':'XMLHttpRequest',
            })
        resp = self._s.get(down_url,params=params)
        params.update({'ping':1})
        resp2 = self._s.get(down_url,params=params)
        self.get_all_song(resp2.json()['url'],str(song_id))
        return resp2.json()['url']

    def get_all_song_list(self):
        page_url_template = 'http://www.xiami.com/space/{0[name]}/u/{0[user]}/page/%d'.format(self.album)
        file_path = self.base_path +'id_list.txt'
        url_path =self.base_path +'url_list.txt'
        if not os.path.isdir(self.base_path):
            os.makedirs(self.base_path)
        # if not os.path.isfile(file_path):
            # logging.debug('read html file from cache. filepath: {filepath}'.format(filepath=file_path))
        with open(url_path, 'w') as u:
            with open(file_path, 'w') as f:
                for i in range(1,3):
                    # try:
                    page_url = page_url_template%i
                    song_list = self.get_song_list(page_url)
                    f.write("\n".join(song_list))
                    f.write("\n")
                    url_list = list(map(self.get_song_url,song_list))
                    u.write("\n".join(url_list))
                    u.write("\n")
                    # except:
                    #     pass  

    def get_all_song(self,url,file_id):
            song_res = self._s.get(url,stream = True)
            # print(song_res.headers)
            # length = song_res.headers['Content-Length']
            print(song_res.headers['content-disposition'])
            name = unquote_to_bytes(song_res.headers['content-disposition'].split('"')[1])
            print(name.decode('utf-8'))
            with open(name.decode('utf-8'),'wb') as f:
                for chunk in song_res.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                f.write(b's')
 

t=Tags()
t.get_all_song_list()
# pool = Pool(args.thread)
# threads = []
# PAGE_MAX = 20