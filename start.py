#! /usr/bin/env python
from CellCycle.Settings.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper
from CellCycle.MemoryModule.MemoryManagement import startMemoryTask, Command, getRequest, setRequest, killProcess
from threading import Thread

SETTINGSFILEPATH = "./config.txt"

# read settings from config.txt
settings = SettingsManager().readConfigurationFromFile(SETTINGSFILEPATH)

# setup logger. to write messages: logger.warning("hello warning"), logger.exception(""), logger.debug("Hi,I'm a bug")
logger = LoggerHelper(settings).logger

# start memory task. there's a thread for set/control requests, and n threads for get. getterNumber is a setting
setMasterPipe, getMasterPipeList = startMemoryTask(settings, logger)
setSlavePipe, getSlavePipeList = startMemoryTask(settings, logger)

#usage example
setRequest(setMasterPipe, "12", "333asd")
setRequest(setMasterPipe, "1", "asadasdasdsd")
import time
time.sleep(1)
print getRequest(getSlavePipeList[0], 1)
print getRequest(getMasterPipeList[0], 1)
killProcess(setMasterPipe)
killProcess(setSlavePipe)
