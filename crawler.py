import bs4
from faker import Factory
import requests
import json
import time
import re
import os
import sys
from bs4 import BeautifulSoup
import io
from itertools import count
from collections import namedtuple
from urllib.parse import unquote,unquote_to_bytes
from log_main import log

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
    # log.debug(resp.text)
    if result_json['status'] != True:
        log.error("login failed")
    else:
        result_data = result_json['data']
        user_id,nick_name = result_data.get('user_id'),result_data.get('nick_name')
    return s,user_id

class Download(object):
    """docstring for Download"""
    def __init__(self, email, password):
        self._s,self.user_id = get_login_session(email,password)
        self.urlList = {
        'homepage':'http://www.xiami.com',
        'user':'http://www.xiami.com/u/{}',
        'song':'http://www.xiami.com/song/{}',
        'download':'http://www.xiami.com/download/get-link',
        'userAlbum':'http://www.xiami.com/space/{0[name]}/u/{0[user]}/page/%d',
        }
        self.SongInfo = namedtuple('SongInfo',['song_id','song_name','song_album',\
            'song_album_link','singer','singer_link','song_url'])
    def get_response(self, url, *args, **kwargs):
        # 需要处理重定向等信息
        log.debug('get response from %s'%url)
        return self._s.get(url, *args, **kwargs)
    def get_key(page, key):
        pass
        # get specital info about key
    def function():
        pass
        

class GetSong(Download):
    """docstring for GetSong"""
    def __init__(self,email,password):
        super(GetSong, self).__init__(email,password) 

    def get_album_num(self,user):
        album = {'name':'lib-song', 'user':user}
        # 需要选择相册
        page_song_list = []
        for page in count(1):
            url = self.urlList['userAlbum'].format(album)%page
            print(url)
            song_list = self.get_song_list_num(url)
            if song_list:
                page_song_list.append(song_list)
            else:
                log.debug("{}'s album done!!!".format(user))
                break
        return page_song_list

    def get_song_list_num(self, url,status = ['0','1']):
        page_id = int(url[-1])
        if page_id != 1:
            page_pre = url[:-1]+str(page_id-1)
        else:
            page_pre = url
        self._s.headers.update({
            'Referer':url,
        })
        page = self.get_response(url).text
        soup = BeautifulSoup(page, 'html.parser')
        tr_list = soup.find_all('tr',attrs={"data-playstatus": status})
        song_list = []
        pattern = r'[\d]+'
        if not tr_list:
            return None
        for song in tr_list:
            song_id = re.search(pattern,song['id']).group(0)
            song_list.append(song_id)
        return song_list

    def get_page(self,song_id, urlType = None):
        url = self.urlList[urlType].format(song_id)
        # 需要处理重定向等信息
        return self.get_response(url)
        
    def get_user_id(self, song_id, urlType = 'song'):
        page = self.get_page(song_id, urlType).text
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find(attrs={"id": "song_fans_block"})
        userList = table.find_all('a')
        userAll =set()
        if userList:
            for user in userList:
                if user.get('name_card'):
                    userAll.add(user.get('name_card'))
            return userAll
        else:
            return

    def get_song_all(self, song_id):
        song_all = [song_id]
        song_all.extend(self.get_song_info(song_id))
        song_all.append(self.get_song_url(song_id))
        print(song_all)
        return self.SongInfo._make(song_all)
        
    def get_song_info(self, song_id, urlType = 'song'):
        page = self.get_page(song_id, urlType).text
        soup = BeautifulSoup(page, 'html.parser')
        infoList = []
        song_name = ''.join(soup.find(id = 'title').strings).strip()
        infoList.append(song_name)
        table = soup.find('table',attrs={"id": "albums_info"})
        for tr in table.children:
            itemValue = tr.find('a')
            try:
                href = itemValue['href']
                title = itemValue['title']
                infoList.extend([title,href])
            except TypeError as e:
                log.exception("fail to get")      
        return infoList

    def get_song_url(self,song_id):
        tmp = ''.join(str(time.time()).split('.'))[:13]
        param={
            '_':tmp,
            'type':'song',
            'id': str(song_id),
            'quality':2,
        }
        url = self.urlList['download']
        self._s.headers.update({
            'Referer':'http://www.xiami.com/song/{}'.format(song_id),
            # 'X-Requested-With':'XMLHttpRequest',
            })
        resp = self.get_response(url,params=param)
        param.update({'ping':1})
        resp2 = self.get_response(url,params=param)
        # self.get_song_mp3(resp2.json()['url'],str(song_id))
        return resp2.json()['url']

    def get_song_mp3(self,url,file_id):
        song_res = self.get_response(url,stream = True)
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
    def test(self):
        # self.get_album_num()
        # self.get_song_url('1772482838')
        self.get_song_all('1772482838')
        # self.get_song_info('')
        # self.get_user_id('1772482838')
                       
if __name__ == '__main__':
    t = GetSong(email,password)
    t.test()
        