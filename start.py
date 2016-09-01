#! /usr/bin/env python
from CellCycle.Settings.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper
from CellCycle.MemoryModule.MemoryManagement import startMemoryTask, Command
from threading import Thread

SETTINGSFILEPATH = "./config.txt"

# read settings from config.txt
settings = SettingsManager().readConfigurationFromFile(SETTINGSFILEPATH)

# setup logger. to write messages: logger.warning("hello warning"), logger.exception(""), logger.debug("Hi,I'm a bug")
logger = LoggerHelper(settings).logger

# start memory thread
setPipe, getPipeList = startMemoryTask(settings, logger)

#usage example
setPipe.send(Command(0, "12", "333"))
setPipe.send(Command(0, 1, "3555553"))
import time
time.sleep(1)
getPipeList[0].send(Command(1, "12"))
print getPipeList[0].recv()
