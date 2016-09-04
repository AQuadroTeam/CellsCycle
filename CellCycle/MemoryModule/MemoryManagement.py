import Queue
from multiprocessing import Process, Pipe
from cPickle import loads, dumps
from threading import Thread


SETCOMMAND = 0
GETCOMMAND = 1
SHUTDOWNCOMMAND = -1
TRANSFERMEMORY = 2

def startMemoryTask(settings, logger):
    #get pipe
    getterNumber = settings.getGetterThreadNumber()
    getterNumber = getterNumber if getterNumber>0 else 1
    memorySideGetPipeList = []
    clientSideGetPipeList = []
    for i in range(getterNumber):
        m,c = Pipe()
        memorySideGetPipeList.append(m)
        clientSideGetPipeList.append(c)

    # set pipe
    memorySideSetPipe, clientSideSetPipe = Pipe()

    #create new process
    p = Process(name='python-CCMemory',target=_memoryTask, args=(settings, logger, memorySideSetPipe, memorySideGetPipeList))
    p.start()

    return clientSideSetPipe, clientSideGetPipeList


def _memoryTask(settings, logger, pipe_set, pipe_get_list):
    from Cache import Slab, CacheSlubLRU
    # grab settings
    slabSize = settings.getSlabSize()
    preallocatedPool = settings.getPreallocatedPool()
    getterNumber = settings.getGetterThreadNumber()

    # initialize cache
    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab

    #log
    logger.debug("Memory Process initialized:" + str(preallocatedPool) + "B, get# = " + str(getterNumber))

    for pipe in pipe_get_list:
        th = Thread(name='MemoryGetter',target=_getThread, args=(logger, cache, pipe))
        th.start()

    _setThread(logger, cache, pipe_set)

def _setThread(logger, cache, pipe):
    while True:
        command = loads(pipe.recv_bytes())
        logger.debug("received set command: " + str(command))
        if command.type == SETCOMMAND:
            cache.set(command.key, command.value)
        if command.type == SHUTDOWNCOMMAND:
            logger.debug("shutdown command")
            import os, signal
            os.kill(os.getpid(), signal.SIGTERM)
            return
        if command.type == TRANSFERMEMORY:
            pipe.send_bytes(dumps(cache.transferMemory()))

def _getThread(logger,cache, pipe):
    while True:
        command = loads(pipe.recv_bytes())
        logger.debug( "received get command: " + str(command))
        if command.type == GETCOMMAND:
            v=cache.get(command.key)
            pipe.send_bytes(dumps(v))
            pipe.flush()
        if command.type == SHUTDOWNCOMMAND:
            return

def getRequest(pipe, key):
    pipe.send_bytes(dumps(Command(GETCOMMAND, key)))
    return loads(pipe.recv_bytes())

def setRequest(pipe, key, value):
    pipe.send_bytes(dumps(Command(SETCOMMAND, key, value)))

def killProcess(pipe):
    pipe.send_bytes(dumps(Command(SHUTDOWNCOMMAND)))

def transferRequest(pipe):
    pipe.send_bytes(dumps(Command(TRANSFERMEMORY)))
    return loads(pipe.recv_bytes())

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
