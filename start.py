#! /usr/bin/env python
from CellCycle.Settings.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper
from CellCycle.ListThread.ReadingThread import ReadingThread
from CellCycle.ListThread.WritingThread import WritingThread
from threading import Event
from CellCycle.ListThread.DeadReader import DeadReader
from CellCycle.ListThread.DeadWriter import DeadWriter
import time
import multiprocessing
from CellCycle.MemoryModule.MemoryManagement import startMemoryTask, Command, getRequest, setRequest, killProcess, transferRequest
from threading import Thread

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

    # start memory task. there's a thread for set/control requests, and n threads for get. getterNumber is a setting
    url_worker, url_set, url_setPort, url_getPort = startMemoryTask(settings, logger, True)
    url_worker_slave, url_set_slave, url_setPort_slave, url_getPort_slave = startMemoryTask(settings, logger, False)


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
