import os
import sqlite3
import logging
from crawler import *
from ThreakPool import flatten


class Database(object):
    def __init__(self, dbFile):
        try:
            self.conn = sqlite3.connect(dbFile, isolation_level=None, check_same_thread = False) #让它自动commit，效率也有所提升. 多线程共用
            with open('schema.sql','rt') as f:
                schema = f.read()
            conn.executescript(schema)
            print('Inserting inital data')
        except Exception, e:
            self.conn = None

    def isConn(self):
        if self.conn:
            return True
        else:
            return False

    def save_song(self, queue, e):
        e.wait()
        log.debug('write into db.SONG')
        song = []
        while not queue.empty():                
            item = queue.get()
            song.append(item)
            queue.task_done()
        if self.conn:
            cursor = conn.cursor()
                # Insert the objects into the database
            #     SongInfo = namedtuple('SongInfo',['song_id','song_name','song_album',\
            # 'song_album_link','singer','singer_link','song_url'])
                cursor.executemany('''insert into SONG
                 (SONG_ID, SONG_NAME, SONG_ALBUM, SONG_ALBUM_LINK, 
                 SINGER, SINGER_LINK, SONG_URL) values
                 (?,?,?,?,?,?,?)''',song)
            else :
                raise sqlite3.OperationalError,'Database is not connected. Can not save Data!'
    def save_user(self, queue, e):
        e.wait()
        log.debug('write into db.USER and db.SEARCH')
        user_song = []
        user = set()
        while not queue.empty():                
            item = queue.get()
            song.append(item)
            user.add(item[0])
            queue.task_done()
        if self.conn:
            cursor = conn.cursor()
                # Insert the objects into the database
            #     SongInfo = namedtuple('SongInfo',['song_id','song_name','song_album',\
            # 'song_album_link','singer','singer_link','song_url'])
                cursor.executemany('''insert into SEARCH
                 (SONG_ID, USER_ID) values
                 (?,?)''',user_song)
                cursor.executemany('''insert into SEARCH
                 (USER_ID) values
                 (?)''',user_song)
            else :
                raise sqlite3.OperationalError,'Database is not connected. Can not save Data!'

    def close(self):
        if self.conn:
            self.conn.close()
        else :
            raise sqlite3.OperationalError, 'Database is not connected.'