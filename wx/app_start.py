import multiprocessing

import contact_scheduler as contact
import msg_scheduler as msg
import os
from multiprocessing.pool import ThreadPool
import time

if __name__=='__main__':
    msg.func()
    # msgProcess=multiprocessing.Process(target=msg.func())
    #
    # contactProcess=multiprocessing.Process(target=contact.func())
    #
    # msgProcess.start()
    # contactProcess.start()