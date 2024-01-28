import sched
from datetime import datetime
import os
from threading import Thread
import sqllite_msg as sqllite
from multiprocessing.pool import ThreadPool
import config as config
import time

oldTimestamp=int(time.time())-15

# 初始化sched模块的scheduler类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)


def get_file(path):
    global oldTimestamp
    # 创建一个空列表
    files = os.listdir(path)
    # files.sort() #排序
    items=[]
    for file in files:
        if not os.path.isdir(path + file):  # 判断该文件是否是一个文件夹
            f_name = str(file)
            if f_name.endswith(".db") and 'msg' in f_name:
                filename = path + f_name  # 创建线程对象
                items.append(filename)
    pool = ThreadPool(10)  # 创建一个线程池
    pool.map(lambda x:decryptTask(x,oldTimestamp), items)  # 往线程池中填线程
    pool.close()  # 关闭线程池，不再接受线程
    pool.join()
    oldTimestamp=int(time.time())

def decryptTask(filename,oldTimestamp):
    # print(filename)
    sqllite.decrypt(config.filePath, filename.rsplit("/", 1)[1],oldTimestamp)
    # sqllite.wx_contact('/Users/guojiewei/wx/', 'decrypt_wccontact_new2.db')


def execute(filePath):
    get_file(filePath)


def task(inc):
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    print(ts)
    execute(config.filePath);
    schedule.enter(inc, 0, task, (inc,))


def func(inc=1):
    # enter四个参数分别为：
    # 间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数、给该触发函数的参数（tuple形式）
    schedule.enter(0, 0, task, (inc,))
    schedule.run()


if __name__ == '__main__':
    func()
