import Queue
from multiprocessing import Process, Pipe
from cPickle import loads, dumps
from threading import Thread
import zmq
from time import time, sleep

SETCOMMAND = 0
GETCOMMAND = 1
SHUTDOWNCOMMAND = -1
TRANSFERMEMORY = 2
NEWMASTER = 3

def startMemoryTask(settings, logger, master):



    url_getBackend = "inproc://get_memory" + ("master" if master else "slave")
    url_setBackend = "inproc://set_memory" + ("master" if master else "slave")
    url_setFrontend = "tcp://*:" + str(settings.getMasterSetPort() if master else settings.getSlaveSetPort())
    url_getFrontend = "tcp://*:" + str(settings.getMasterGetPort() if master else settings.getSlaveGetPort())

    #create new process
    processName = "python-CCMemoryMaster" if master else "python-CCMemorySlave"
    p = Process(name=processName,target=_memoryTask, args=(settings, logger,master, url_setFrontend, url_getFrontend, url_getBackend, url_setBackend))
    p.start()

    return url_getBackend, url_setBackend, url_setFrontend, url_getFrontend


def _memoryTask(settings, logger,master, url_setFrontend, url_getFrontend, url_getBackend, url_setBackend):
    from Cache import Slab, CacheSlubLRU
    # grab settings
    slabSize = settings.getSlabSize()
    preallocatedPool = settings.getPreallocatedPool()
    getterNumber = settings.getGetterThreadNumber()

    # initialize cache
    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab

    #log
    logger.debug("Memory Process initialized:" + str(preallocatedPool) + "B, get# = " + str(getterNumber))

    # Prepare our context and sockets
    context = zmq.Context.instance()
    # Socket to talk to get
    socketGetFrontend = context.socket(zmq.ROUTER)
    socketGetFrontend.bind(url_getFrontend)

    # Socket to talk to workers
    socketGetBackend = context.socket(zmq.DEALER)
    socketGetBackend.bind(url_getBackend)

    timing = {}
    timing["getters"] = []
    timing["setters"] = [-1]

    Thread(name='MemoryGetProxy',target=_proxyThread, args=(logger, master, socketGetFrontend, socketGetBackend, url_getFrontend, url_getBackend)).start()

    for i in range(getterNumber):
        timing["getters"].append(-1)
        th = Thread(name='MemoryGetter',target=_getThread, args=(i,logger, cache,master,url_getBackend, timing))
        th.start()

    slaveSetQueue = Queue.Queue()
    hostState = HostUrlState()

    Thread(name='MemoryPerformanceMetricator',target=_memoryMetricatorThread, args=(logger, cache, settings, timing)).start()
    Thread(name='MemorySlaveSetter',target=_setToSlaveThread, args=(logger, cache,master,url_getBackend, slaveSetQueue, hostState)).start()

    _setThread(logger, cache,master,url_setFrontend,slaveSetQueue, hostState, timing)


def _memoryMetricatorThread(logger, cache, settings, timing):
    logger.debug("Metricator thread alive")
    period = 10
    while True:
        sleep(period)
        logger.debug("Waiting time for setter: " + str(timing["setters"][0]))
        for metr in timing["getters"]:
            logger.debug("Waiting time for getters: " + str(metr) )




def _proxyThread(logger, master, frontend, backend, url_frontend, url_backend):
    logger.debug("Routing from " + url_frontend + " to " + url_backend)
    zmq.proxy(frontend, backend)

def _setToSlaveThread(logger, cache, master,url, queue, hostState):
    while True:
        objToSend = queue.get()
        slaveAddress = hostState.getSlaveUrl()
        if(slaveAddress != None):
            try:
                setRequest(slaveAddress, objToSend.key, objToSend.value)
            except Exception as e:
                logger.warning(str(e))

def _setThread(logger, cache, master, url,queue,  hostState, timing):
    logger.debug("Listening in new task for set on " + url)
    context = zmq.Context.instance()
    socket = context.socket(zmq.PULL)
    socket.bind(url)

    timing["setters"] = []
    timing["setters"].append(TimingMetricator(0.5, 0.5))

    while True:
        timing["setters"][0].startWaiting()

        command = loads(socket.recv())
        timing["setters"][0].startWorking()

        #logger.debug("received set command: " + str(command))
        if command.type == SETCOMMAND:
            queue.put(Command(command.type, command.key, command.value, command.address))
            cache.set(command.key, command.value)
        if command.type == SHUTDOWNCOMMAND:
            logger.debug("shutdown command")
            import os, signal
            os.kill(os.getpid(), signal.SIGTERM)
            return
        if command.type == TRANSFERMEMORY:
            logger.debug("Transferring memory to " + str(command.address) + "....")
            context = zmq.Context.instance()
            socketTM = context.socket(zmq.PUSH)
            socketTM.connect(command.address)
            for data in cache.cache.iteritems():
                socketTM.send(dumps(Command(SETCOMMAND,data[0],data[1].getValue(data[0]))))
            socketTM.close()
            logger.debug("Transfer complete!")
        if command.type == NEWMASTER:
            #do something with command and hostState
            #command.optional --> hostState
            a = 2
        timing["setters"][0].stopWorking()


def _getThread(index, logger,cache, master, url, timing):
    logger.debug("Listening in new task for get on " + url)
    context = zmq.Context.instance()
    socket = context.socket(zmq.REP)
    socket.connect(url)

    timing["getters"][index] = TimingMetricator(0.5, 0.5)

    while True:
        timing["getters"][index].startWaiting()
        command = loads(socket.recv())
        timing["getters"][index].startWorking()

        #logger.debug( "received get command: " + str(command))
        if command.type == GETCOMMAND:
            v=cache.get(command.key)
            socket.send(dumps(v))
        #if command.type == SHUTDOWNCOMMAND:
        #    return
        timing["getters"][index].stopWorking()

# client operations
def getRequest(url, key):
    context = zmq.Context.instance()
    socket = context.socket(zmq.REQ)
    socket.connect(url)

    socket.send(dumps(Command(GETCOMMAND, key)))
    v = loads(socket.recv())
    socket.close()
    return v

def setRequest(url, key, value):
    context = zmq.Context.instance()
    socket = context.socket(zmq.PUSH)
    socket.connect(url)

    socket.send(dumps(Command(SETCOMMAND, key, value)))
    socket.close()

def killProcess(url):
    context = zmq.Context.instance()
    socket = context.socket(zmq.PUSH)
    socket.connect(url)

    socket.send(dumps(Command(SHUTDOWNCOMMAND)))
    socket.close()

def transferRequest(url, dest):
    context = zmq.Context.instance()
    socket = context.socket(zmq.PUSH)
    socket.connect(url)

    socket.send(dumps(Command(TRANSFERMEMORY, address=dest)))
    socket.close()

def newMasterRequest(url, hostInformations):
    context = zmq.Context.instance()
    socket = context.socket(zmq.PUSH)
    socket.connect(url)
    command = Command(SETCOMMAND)
    command.optional = hostInformations
    socket.send(dumps(command))
    socket.close()

def standardnewMasterRequest(settings, hostInformations, host="localhost"):
    url_setPort = "tcp://"+host+":" + str(settings.getMasterSetPort())
    return newMasterRequest(url_setPort, hostInformations)

def standardMasterSetRequest(settings, key, value, host="localhost"):
    url_setPort = "tcp://"+host+":" + str(settings.getMasterSetPort())
    return setRequest(url_setPort, key, value)

def standardMasterGetRequest(settings, key, host="localhost"):
    url_getPort = "tcp://"+host+":" + str(settings.getMasterGetPort())
    return getRequest(url_getPort, key)

def standardSlaveSetRequest(settings, key, value, host="localhost"):
    url_setPort = "tcp://"+host+":" + str(settings.getSlaveSetPort())
    return setRequest(url_setPort, key, value)

def standardSlaveGetRequest(settings, key, host="localhost"):
    url_getPort = "tcp://"+host+":" + str(settings.getSlaveGetPort())
    return getRequest(url_getPort, key)

def standardKillRequest(settings, host="localhost"):
    url_setPort = "tcp://"+host+":" + str(settings.getMasterSetPort())
    return killRequest(url_setPort)

def standardTransferRequest(settings, dest="localhost", host="localhost"):
    url_setPort = "tcp://"+host+":" + str(settings.getMasterSetPort())
    dest = "tcp://"+dest+":" + str(settings.getSlaveSetPort())
    return transferRequest(url_setPort, dest)

class Command(object):
    def __init__(self, type, key=None, value=None, address=None, optional=None):
        self.type = int(type)
        self.key = key
        self.value = value
        self.address = address
        self.optional = optional
    def __str__(self):
        return "type: "+ str(self.type) + ", key: "+ str(self.key) + ", value: " + str(self.value)

class HostUrlState(object):
    def __init__(self):
        self.masterSetUrl = None
        self.masterGetUrl = None
        self.slaveSetUrl = None
        self.slaveGetUrl = None
    def getSlaveUrl(self):
        return self.slaveSetUrl

# only for benchamrk
def startMemoryTaskForTrial(preallocatedPool, slabSize, logger, pipe_set, pipe_get):

    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab
    for pipe in pipe_get:
        th = Thread(target=getThread, args=(cache, pipe))
        th.start()

    setThread(cache, pipe_set)

class TimingMetricator(object):
    """docstring forTimingMetricator."""
    def __init__(self, alpha, beta):
        self.startWaitingTime = 0
        self.startWorkingTime = 0
        self.stopWorkingTime = 0
        self.alpha = alpha
        self.beta = beta
        self.meanWaitingRatio = 0

    def __str__(self):
        return str(self.meanWaitingRatio)

    def startWorking(self):
        self.startWorkingTime = time()

    def startWaiting(self):
        self.startWaitingTime = time()

    def stopWorking(self):
        self.stopWorkingTime = time()
        print self.startWaitingTime
        print self.startWorkingTime
        print self.stopWorkingTime
        wait = self.startWorkingTime - self.startWaitingTime
        period = self.stopWorkingTime - self.startWaitingTime
        self.meanWaitingRatio = wait / period * self.alpha + self.beta * self.meanWaitingRatio
