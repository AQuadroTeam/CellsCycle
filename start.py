#! /usr/bin/env python
from CellCycle.Settings.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper
from CellCycle.MemoryThread.MemoryThread import startMemoryThread
from CellCycle.ListThread.ReadingThread import ReadingThread
from CellCycle.ListThread.WritingThread import WritingThread
from threading import Event
from CellCycle.ListThread.DeadReader import DeadReader
from CellCycle.ListThread.DeadWriter import DeadWriter
import time
import multiprocessing

SETTINGSFILEPATH = "./config.txt"
DELAY = 0.3


# read settings from config.txt
settings = SettingsManager().readConfigurationFromFile(SETTINGSFILEPATH)

# setup logger. to write messages: logger.warning("hello warning"), logger.exception(""), logger.debug("Hi,I'm a bug")
logger = LoggerHelper(settings).logger

# start memory thread
# Thread(name='MemoryThread',target=startMemoryThread, args=[settings, logger]).start()

# Create conditions
event1 = Event()
event2 = Event()
event3 = Event()

# Create new threads

# Create different processes

# The order is different if we use PUB-SUB

def worker(num):

    if num == 1:
        thread1 = DeadReader([1,5555], [3,5557], [2,5556], [3,5557], [0, 33], [33,66], logger, event1, DELAY)
        #thread4 = WritingThread([1,5555], [3,5557], [2,5556], [3,5557], [0, 127], [0, 127], logger, event1, DELAY)
        thread7 = DeadWriter([1,5555], [3,5557], [2,5556], [3,5557], [0, 127], [0, 127], logger, event1, DELAY)

        thread7.start()
        time.sleep(0.1)
        #thread4.start()
        thread1.start()
        thread1.join()
        print 'Finishing PROCESS ' + str(num)

    elif num == 2:
        thread2 = DeadReader([2,5556], [1,5555], [3,5557], [1,5555], [33, 66], [66,99], logger, event2, DELAY)
        #thread5 = WritingThread([2,5556], [1,5555], [3,5557], [1,5555], [0, 127], [0, 127], logger, event2, DELAY)
        thread8 = DeadWriter([2,5556], [1,5555], [3,5557], [1,5555], [0, 127], [0, 127], logger, event2, DELAY)

        thread8.start()
        time.sleep(0.1)
        #thread5.start()
        thread2.start()
        thread2.join()
        print 'Finishing PROCESS ' + str(num)

    elif num == 3:
        thread3 = DeadReader([3,5557], [2,5556], [1,5555], [2,5556], [66, 99], [0, 33], logger, event3, DELAY)
        #thread6 = WritingThread([3,5557], [2,5556], [1,5555], [2,5556], [0, 127], [0, 127], logger, event3, DELAY)
        thread9 = DeadWriter([3,5557], [2,5556], [1,5555], [2,5556], [0, 127], [0, 127], logger, event3, DELAY)

        thread9.start()
        time.sleep(0.1)
        #thread6.start()
        thread3.start()
        thread3.join()
        print 'Finishing PROCESS ' + str(num)

    return

if __name__ == '__main__':
    jobs = []
    for i in range(1,4):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()



# Start new Threads
'''
thread2.start()
thread3.start()

thread4.start()
thread5.start()
thread6.start()

thread7.start()
thread8.start()
thread9.start()
'''

print "Exiting Main Thread"