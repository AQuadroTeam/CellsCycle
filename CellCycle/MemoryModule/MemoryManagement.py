import Queue
from multiprocessing import Process, Pipe
from cPickle import loads, dumps
from threading import Thread
import zmq


SETCOMMAND = 0
GETCOMMAND = 1
SHUTDOWNCOMMAND = -1
TRANSFERMEMORY = 2

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


    Thread(name='MemoryGetProxy',target=_proxyThread, args=(logger, master, socketGetFrontend, socketGetBackend, url_getFrontend, url_getBackend)).start()

    for _ in range(getterNumber):
        th = Thread(name='MemoryGetter',target=_getThread, args=(logger, cache,master,url_getBackend))
        th.start()

    _setThread(logger, cache,master,url_setFrontend)


def _proxyThread(logger, master, frontend, backend, url_frontend, url_backend):
    logger.debug("Routing from " + url_frontend + " to " + url_backend)
    zmq.proxy(frontend, backend)

def _setThread(logger, cache, master, url):
    logger.debug("Listening in new task for set on " + url)
    context = zmq.Context.instance()
    socket = context.socket(zmq.PULL)

    socket.bind(url)

    while True:
        command = loads(socket.recv())
        #logger.debug("received set command: " + str(command))
        if command.type == SETCOMMAND:
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

def _getThread(logger,cache, master, url):
    logger.debug("Listening in new task for get on " + url)
    context = zmq.Context.instance()
    socket = context.socket(zmq.REP)
    socket.connect(url)

    while True:
        command = loads(socket.recv())
        #logger.debug( "received get command: " + str(command))
        if command.type == GETCOMMAND:
            v=cache.get(command.key)
            socket.send(dumps(v))
        #if command.type == SHUTDOWNCOMMAND:
        #    return

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


class Command(object):
    def __init__(self, type, key=None, value=None, address=None):
        self.type = int(type)
        self.key = key
        self.value = value
        self.address = address
    def __str__(self):
        return "type: "+ str(self.type) + ", key: "+ str(self.key) + ", value: " + str(self.value)



# only for benchamrk
def startMemoryTaskForTrial(preallocatedPool, slabSize, logger, pipe_set, pipe_get):

    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab
    for pipe in pipe_get:
        th = Thread(target=getThread, args=(cache, pipe))
        th.start()

    setThread(cache, pipe_set)