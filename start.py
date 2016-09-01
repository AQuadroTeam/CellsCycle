#! /usr/bin/env python
from CellCycle.Settings.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper
from CellCycle.MemoryThread.MemoryThread import startMemoryThread
from CellCycle.ListThread.ReadingThread import ReadingThread
from CellCycle.ListThread.WritingThread import WritingThread
from threading import Event

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

thread1 = ReadingThread([1,5555], [3,5557], [2,5556], [], [0, 33], [33,66], logger, event1, DELAY)
thread2 = ReadingThread([2,5556], [1,5555], [3,5557], [], [33, 66], [66,99], logger, event2, DELAY)
thread3 = ReadingThread([3,5557], [2,5556], [1,5555], [], [66, 99], [0, 33], logger, event3, DELAY)

thread4 = WritingThread([1,5555], [3,5557], [2,5556], [], [0, 127], [0, 127], logger, event1, DELAY)
thread5 = WritingThread([2,5556], [1,5555], [3,5557], [], [0, 127], [0, 127], logger, event2, DELAY)
thread6 = WritingThread([3,5557], [2,5556], [1,5555], [], [0, 127], [0, 127], logger, event3, DELAY)

# Start new Threads
thread1.start()
thread2.start()
thread3.start()

thread4.start()
thread5.start()
thread6.start()

print "Exiting Main Thread"