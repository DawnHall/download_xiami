"""
threadPool.py
该模块包含工作线程与线程池的实现。
"""
from log_main import log
import traceback
from threading import Thread, Lock
import functools
from itertools import cycle, repeat
from queue import Queue, Empty, Full

class QueueResult(Queue):
    """docstring for QueueResult"""
    def __init__(self,event = None,**kwargs):
        self.event = event
        super(QueueResult,self).__init__(**kwargs)
    def put(self,item):
        try:
            super(QueueResult,self).put(item)   
        except Full as e:
            log.exception('queue full!!!')
            event.set()            
            raise e

class QueueCheck(Queue):
    """docstring for QueueCheck"""
    def __init__(self,**kwargs):
        super(QueueCheck,self).__init__(**kwargs)
        self.item_list = set()
    def put(self,item):
        try:
            for x in flatten(item):
                if x in self.item_list:
                    continue
                else:
                    super(QueueCheck,self).put(x)   
                    self.item_list.add(x)
        except Full as e:
            log.exception('queue full!!!')
            raise e
    def get(self):
        try:
            return super(QueueCheck,self).get()
        except Empty as e:
            log.exception("clear q")
            self.item_list.clear()
            raise e

class Dispatcher(object):
    """docstring for Dispatcher"""
    def __init__(self,threadPool):
        super(Dispatcher, self).__init__()
        self.pool = threadPool
        self.dispatch = dict()
        self.match()
        self.funcList = []

    def task_init(self, f, *args,**kwargs):
        kwargs,toDoQueue,resultQueue= self.decorate(**kwargs)
        self.funcList.append((f, args, kwargs, toDoQueue, resultQueue))

    def decorate(self,**kwargs):
        toDoQueue = self.dispatch.get(kwargs.pop('get'))
        resultQueue = self.dispatch.get(kwargs.pop('put'))
        return (kwargs,toDoQueue,resultQueue)

    def match(self):
        self.dispatch = {
        'user':self.pool.userQueue,
        'song_id':self.pool.songIdQueue,
        'song':self.pool.songAllQueue,
        'song_user':self.pool.songUserQueue
        }


class Worker(Thread):
    def __init__(self, pool, item, record = False):
        Thread.__init__(self)
        self.pool = pool
        self.item = item
        self.state = 'RUN'
        self.record = record
        self.start()

    def stop(self):
        self.state = 'STOP'
        # for q in self.pool.queue:
        #     if q.qsize()>100:
        #         pass
                # self.state = 'STOP'
        pass
    def run(self):
        while 1:
            if self.state == 'STOP':
                break
            f, args, kwargs, toDoQueue, resultQueue = self.item
            try:
                taskIn = toDoQueue.get() 
                result = f(taskIn, *args, **kwargs)
                if result:
                    resultQueue.put(result)
                if self.record:
                    self.pool.add_record(taskIn, result)
                toDoQueue.task_done()
            except Exception as e:
                log.exception(msg = e)
                continue

class ThreadPool(object):
    def __init__(self, threadNum):
        self.pool = [] #线程池
        self.threadNum = threadNum  #线程数
        self.lock = Lock() #线程锁
        self.running = 0    #正在run的线程数
        self.userQueue = QueueCheck()
        self.songIdQueue = QueueCheck()
        self.songAllQueue = QueueResult(block = False)
        self.songUserQueue =  QueueResult(block = False)
        self.dispatch = Dispatcher(self)
  
    def start_threads(self,queue = None,itemIn = None):
        if queue == 'user':
            print("user queue")
            self.userQueue.put(itemIn)
        elif queue == 'song_id':
            print("song queue")
            self.songIdQueue.put(itemIn)
        else:
            raise Exception
        try:
            for cnt, item in zip(range(self.threadNum),cycle(self.dispatch.funcList)):
                # 特定的func需要对input和output单独输出，这里是get_album_num
                if cnt%len(self.dispatch.funcList) == 0:
                    self.pool.append(Worker(self,item,record = True))
                else:
                    self.pool.append(Worker(self,item))
        except Empty as e:
            log.exception('fail')
    def add_record(self,itemIn,itemOut):
         for item in flatten(itemOut):
            self.songUserQueue.put((itemIn,item))                  

def flatten(nested):
    try:
        try:
            nested + ''
        except TypeError:
            pass
        else:
            raise TypeError
        for sublist in nested:
            for element in flatten(sublist):
                yield element
    except TypeError:
        yield nested

# class SongResult(object):
#     """docstring for SongResult"""
#     def __init__(self, song_id,**kargs):
#         super(SongResult, self).__init__()
#         self.song_id = song_id
#         self.ready = False
#         try:   
#             self.url= kargs['url']
#             self.info=kargs['info']
#         except KeyError:
#             pass
#         self.ready = self.readyTest()
#     def readyTest(self): 
#         if self.url and self.info:
#             return True
#         return False    