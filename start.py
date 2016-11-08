#! /usr/bin/env python
from CellCycle.Settings.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper
from CellCycle.MemoryModule.MemoryManagement import startMemoryTask, getRequest, setRequest, killProcess, transferRequest
from CellCycle.ExtraCycleInterface.ExtraCycle import startExtraCycleListeners
from CellCycle.ChainModule.Generator import Generator

def loadSettings(currentProfile):
    SETTINGSFILEPATH = "./config.txt"

    # read settings from config.txt
    settings = SettingsManager().readConfigurationFromFile(SETTINGSFILEPATH)
    if(currentProfile != None):
        settings.setAwsProfileName(currentProfile["profile_name"])
        settings.setAwsKeyName(currentProfile["key_pair"])
        settings.setGitBranch(currentProfile["branch"])
    return settings


def loadLogger(settings):
    # setup logger. to write messages: logger.warning("hello warning"), logger.exception(""), logger.debug("Hi,I'm a bug")
    logger = LoggerHelper(settings).logger
    return logger

def startApplication(startParams, settings):
    logger = loadLogger(settings)

    logger.debug("Starting with params: " + str(startParams))

    # start memory task. there's a thread for set/control requests, and n threads for get. getterNumber is a setting
    url_worker, url_set, url_setPort, url_getPort = startMemoryTask(settings, logger, True)
    url_worker_slave, url_set_slave, url_setPort_slave, url_getPort_slave = startMemoryTask(settings, logger, False)
    startExtraCycleListeners(settings, logger)

    # Let's start the list communication part
    generator = Generator(logger=logger, settings=settings, json_arg=startParams)
    generator.create_process_environment()


def exampleFillAndTransfer(settings, logger):
    #usage example
    import time
    time.sleep(5)
    url_getPort = "tcp://localhost:" + str(settings.getMasterGetPort())
    url_setPort = "tcp://localhost:" + str(settings.getMasterSetPort())
    url_setPort_slave = "tcp://localhost:" + str(settings.getSlaveSetPort())
    url_getPort_slave = "tcp://localhost:" + str(settings.getSlaveGetPort())
    getRequest(url_getPort, "12")
    setRequest(url_setPort, "12", "333asd")

    setRequest(url_setPort, "1", "asadasdasdsd")
    import time
    time.sleep(1)
    import zmq
    from cPickle import dumps, loads
    from CellCycle.MemoryModule.MemoryManagement import Command, SETCOMMAND
    context = zmq.Context.instance()
    socket = context.socket(zmq.PUSH)
    socket.connect(url_setPort)

    for a in range(1000000):

        socket.send(dumps(Command(SETCOMMAND, str(a), "aaaaaaaaa", address="url_setPort_slave")))
    socket.close()

    print "dovrebbe uscire asad....: " + str(getRequest(url_getPort, 1))
    print "non dovrebbe uscire asdasda...: " + str(getRequest(url_getPort_slave, 1))

    transferRequest(url_setPort, url_setPort_slave)
    time.sleep(10)
    print "sul task principale ho ricevuto con chiave 1 su slave:" + str(getRequest(url_getPort_slave, 1))
    print "sul task principale ho ricevuto con chiave 1 su master: " + str(getRequest(url_getPort, 1))
    killProcess(url_setPort)
    killProcess(url_setPort_slave)

if __name__ == "__main__":
    import sys
    if (len(sys.argv) == 1):
        settings = loadSettings()
    else:
        currentProfile = {}
        currentProfile["profile_name"]  = sys.argv[1]
        currentProfile["key_pair"]  = sys.argv[2]
        currentProfile["branch"] = sys.argv[3]
        settings = loadSettings(currentProfile)

    startApplication("Starting from console",settings)
