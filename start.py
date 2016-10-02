#! /usr/bin/env python
from CellCycle.Settings.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper
from CellCycle.MemoryModule.MemoryManagement import startMemoryTask, Command, getRequest, setRequest, killProcess, transferRequest
from threading import Thread

SETTINGSFILEPATH = "./config.txt"

# read settings from config.txt
settings = SettingsManager().readConfigurationFromFile(SETTINGSFILEPATH)

# setup logger. to write messages: logger.warning("hello warning"), logger.exception(""), logger.debug("Hi,I'm a bug")
logger = LoggerHelper(settings).logger

# start memory task. there's a thread for set/control requests, and n threads for get. getterNumber is a setting
url_worker, url_set, url_setPort, url_getPort = startMemoryTask(settings, logger, True)
url_worker_slave, url_set_slave, url_setPort_slave, url_getPort_slave = startMemoryTask(settings, logger, False)

#usage example
import time
time.sleep(5)
url_getPort = "tcp://localhost:" + str(settings.getMasterGetPort())
print url_getPort
getRequest(url_getPort, "12")
print "primo get"
setRequest(url_setPort, "12", "333asd")

setRequest(url_setPort, "1", "asadasdasdsd")
import time
time.sleep(1)
print getRequest(url_getPort, 1)
print getRequest(url_getPort_slave, 1)
cache = transferRequest(url_setPort)
print len(cache)
print "sul task principale ho ricevuto con chiave 1 su slave:" + str(getRequest(url_getPort_slave, 1))
print "sul task principale ho ricevuto con chiave 1 su master: " + str(getRequest(url_getPort, 1))
killProcess(url_setPort)
killProcess(url_setPort_slave)
