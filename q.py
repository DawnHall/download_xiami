# from queue import Queue, Empty
# class QueueCheck(Queue):
#     """docstring for QueueCheck"""
#     def __init__(self):
#         super(QueueCheck,self).__init__()
#         self.item_list = set()
#     def put(self,item):
#         if item in self.item_list:
#             pass
#         else:
#             super(QueueCheck,self).put(item)
#             self.item_list.add(item)
#     def get(self):
#         try:
#             return super(QueueCheck,self).get()
#         except Empty as e:
#             # log.exception("clear q")
#             self.item_list.clear()
#             raise e
# q = QueueCheck()
# q.put('1')
# q.put('2')
# a = q.get()
# print(a)
# q.task_done()
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

while 1:
    print(flatten([[1,2,[3,4,5]],4,5]))