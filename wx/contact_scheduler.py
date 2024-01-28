import sched
from datetime import datetime
import os
from threading import Thread
import sqllite_contact as sqllite

import config as config
import time

oldTimestampContact=int(time.time())-15


# 初始化sched模块的scheduler类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)


def execute(filePath):
    global oldTimestampContact
    sqllite.decrypt(filePath, 'wccontact_new2.db',oldTimestampContact,False)
    oldTimestampContact=int(time.time())

def executeGroup(filePath):
    global oldTimestampContact
    sqllite.decrypt(filePath, 'group_new.db',oldTimestampContact,True)
    oldTimestampContact=int(time.time())

def task(inc):
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    print('contact_task',ts)
    try:
        execute(config.filePathContact)
        executeGroup(config.filePathGroup)
    except Exception as e:
        print(e)
    schedule.enter(inc, 0, task, (inc,))


def func(inc=30):
    # enter四个参数分别为：
    # 间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数、给该触发函数的参数（tuple形式）
    schedule.enter(0, 0, task, (inc,))
    schedule.run()


if __name__ == '__main__':
    func()
