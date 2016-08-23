#! /usr/bin/env python
from CellCycle.Settings.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper
from CellCycle.MemoryThread.MemoryThread import startMemoryThread
from threading import Thread
from CellCycle.ListThread.ReadingThread import ReadingThread
from CellCycle.ListThread.WritingThread import WritingThread

SETTINGSFILEPATH = "./config.txt"

# read settings from config.txt
settings = SettingsManager().readConfigurationFromFile(SETTINGSFILEPATH)

# setup logger. to write messages: logger.warning("hello warning"), logger.exception(""), logger.debug("Hi,I'm a bug")
logger = LoggerHelper(settings).logger

# start memory thread
# Thread(name='MemoryThread',target=startMemoryThread, args=[settings, logger]).start()

# Create new threads

thread1 = ReadingThread([1,5555], [3,5557], [2,5556], [], [0, 127], [0, 127], logger)
thread2 = ReadingThread([2,5556], [1,5555], [3,5557], [], [0, 127], [0, 127], logger)
thread3 = ReadingThread([3,5557], [2,5556], [1,5555], [], [0, 127], [0, 127], logger)

thread4 = WritingThread([1,5555], [3,5557], [2,5556], [], [0, 127], [0, 127], logger)
thread5 = WritingThread([2,5556], [1,5555], [3,5557], [], [0, 127], [0, 127], logger)
thread6 = WritingThread([3,5557], [2,5556], [1,5555], [], [0, 127], [0, 127], logger)

# Start new Threads
thread1.start()
thread2.start()
thread3.start()

thread4.start()
thread5.start()
thread6.start()

print "Exiting Main Thread"