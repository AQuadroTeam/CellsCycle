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
    p = Process(name='python-CCMemory',target=_memoryTask, args=(settings, logger,master, url_setFrontend, url_getFrontend, url_getBackend, url_setBackend))
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
    # Socket to talk to set
    socketGetFrontend = context.socket(zmq.ROUTER)
    socketGetFrontend.bind(url_getFrontend)
    # Socket to talk to get
    socketSetFrontend = context.socket(zmq.ROUTER)
    socketSetFrontend.bind(url_setFrontend)
    # Socket to talk to workers
    socketGetBackend = context.socket(zmq.DEALER)
    socketGetBackend.bind(url_getBackend)
    socketSetBackend = context.socket(zmq.DEALER)
    socketSetBackend.bind(url_setBackend)

    Thread(name='MemoryGetProxy',target=_proxyThread, args=(logger, master, socketGetFrontend, socketGetBackend, url_getFrontend, url_getBackend)).start()
    Thread(name='MemorySetProxy',target=_proxyThread, args=(logger, master,socketSetFrontend, socketSetBackend,url_setFrontend, url_setBackend )).start()
    for _ in range(getterNumber):
        th = Thread(name='MemoryGetter',target=_getThread, args=(logger, cache,master,url_getBackend))
        th.start()

    _setThread(logger, cache,master,url_setBackend)


def _proxyThread(logger, master, frontend, backend, url_frontend, url_backend):
    logger.debug("Routing from " + url_frontend + " to " + url_backend)
    zmq.proxy(frontend, backend)

def _setThread(logger, cache, master, url):
    logger.debug("Listening in new task for set on " + url)
    context = zmq.Context.instance()
    socket = context.socket(zmq.REP)

    socket.connect(url)

    while True:
        command = loads(socket.recv())
        #logger.debug("received set command: " + str(command)) too heavy
        if command.type == SETCOMMAND:
            cache.set(command.key, command.value)
            socket.send(dumps(0))
        if command.type == SHUTDOWNCOMMAND:
            logger.debug("shutdown command")
            import os, signal
            os.kill(os.getpid(), signal.SIGTERM)
            return
        if command.type == TRANSFERMEMORY:
            print "transferring memory..."
            print "missing"
            print "transfer completed"

def _getThread(logger,cache, master, url):
    logger.debug("Listening in new task for get on " + url)
    context = zmq.Context.instance()
    socket = context.socket(zmq.REP)
    socket.connect(url)

    while True:
        command = loads(socket.recv())
        print "ok"
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
    return loads(socket.recv())

def setRequest(url, key, value):
    context = zmq.Context.instance()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5550")

    socket.send(dumps(Command(SETCOMMAND, key, value)))

def killProcess(url):
    context = zmq.Context.instance()
    socket = context.socket(zmq.REQ)
    socket.connect(url)

    socket.send(dumps(Command(SHUTDOWNCOMMAND)))

def transferRequest(url):
    context = zmq.Context.instance()
    socket = context.socket(zmq.REQ)
    socket.connect(url)

    socket.send(dumps(Command(TRANSFERMEMORY)))


class Command(object):
    def __init__(self, type, key=None, value=None):
        self.type = int(type)
        self.key = key
        self.value = value
    def __str__(self):
        return "type: "+ str(self.type) + ", key: "+ str(self.key) + ", value: " + str(self.value)



# only for benchamrk
def startMemoryTaskForTrial(preallocatedPool, slabSize, logger, pipe_set, pipe_get):

    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab
    for pipe in pipe_get:
        th = Thread(target=getThread, args=(cache, pipe))
        th.start()

    setThread(cache, pipe_set)
