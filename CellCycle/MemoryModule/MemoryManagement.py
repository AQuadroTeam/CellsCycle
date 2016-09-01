from Cache import Slab, CacheSlubLRU
import Queue
from multiprocessing import Process, Pipe
from threading import Thread

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
    p = Process(name='python-CCMemory',target=memoryTask, args=(settings, logger, memorySideSetPipe, memorySideGetPipeList))
    p.start()

    return clientSideSetPipe, clientSideGetPipeList


def memoryTask(settings, logger, pipe_set, pipe_get_list):
    # grab settings
    slabSize = settings.getSlabSize()
    preallocatedPool = settings.getPreallocatedPool()
    getterNumber = settings.getGetterThreadNumber()

    # initialize cache
    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab

    #log
    logger.debug("Memory Process initialized:" + str(preallocatedPool) + "B, get# = " + str(getterNumber))

    for pipe in pipe_get_list:
        th = Thread(name='MemoryGetter',target=getThread, args=(cache, pipe))
        th.start()

    setThread(cache, pipe_set)


def startMemoryTaskForTrial(preallocatedPool, slabSize, logger, pipe_set, pipe_get):

    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab
    for pipe in pipe_get:
        th = Thread(target=getThread, args=(cache, pipe))
        th.start()

    setThread(cache, pipe_set)

def setThread(cache, pipe):
    while True:
        command = pipe.recv()
        print "received set command: " + str(command)
        if command.type == 0:
            cache.set(command.key, command.value)
        if command.type == -1:
            import os
            os.kill()
            return

def getThread(cache, pipe):
    while True:
        command = pipe.recv()
        print "received get command: " + str(command)
        if command.type == 1:
            v=cache.get(command.key)
            pipe.send(v)
        if command.type == -1:
            return




class Command(object):
    def __init__(self, type, key, value=None):
        self.type = int(type)
        self.key = key
        self.value = value
    def __str__(self):
        return "type: "+ str(self.type) + ", key: "+ str(self.key) + ", value: " + str(self.value)
