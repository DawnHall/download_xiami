import logging
import time
from threading import Event
from datetime import datetime
from crawler import GetSong
from ThreadPool import *
from database import Database
db = Database('xiami.db')
eSong = Event()
eSongUser = Event()
# email = ''
# password = ''
t = GetSong(email,password)
pool = ThreadPool(4)
pool.dispatch.task_init(t.get_album_num, get='user', put='song_id')
pool.dispatch.task_init(t.get_user_id, get='song_id', put='user')
pool.dispatch.task_init(t.get_song_all, get='song_id', put='song')
pool.dispatch.task_init(db.save_song, get='song', event = eSong)
pool.dispatch.task_init(db.save_user, get='song_user',event = eSongUser)
# pool.start_threads(queue = 'song_id',itemIn = '1772482838')
pool.start_threads(queue = 'user',itemIn = t.user_id)