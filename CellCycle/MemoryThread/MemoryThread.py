from Cache import Slab, CacheSlubLRU
import Queue
from multiprocessing import Process, Pipe
from threading import Thread

def startMemoryThread(settings, logger):
    parent_conn, child_conn = Pipe()
    p = Process(target=startMemoryTask, args=(settings.getPreallocatedPool(), settings.getSlabSize(), logger, child_conn))

    for i in range(0,10):
        parent_conn.send(Command(0, "chiave", "valore"))
    print "input pronto, il task nasce"
    p.start()
    print "aspetto il task"
    p.join()
    print "e' morto il task"

def startMemoryTask(preallocatedPool, slabSize, logger, pipe_set, pipe_get):

    logger.debug("Hello, I'm a funny thread")


    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab
    for pipe in pipe_get:
        th = Thread(target=startGetThread, args=(cache, pipe))
        th.start()

    while True:
        command = pipe_set.recv()
        if command.type == 0:
            cache.set(command.key, command.value)
        if command.type == 1:
            v=cache.get(command.key)
            pipe_get.send(v if v!=None else 0)
        if command.type == -1:
            return

def startGetThread(cache, pipe_get):
    while True:
        command = pipe_get.recv()
        if command.type == 1:
            v=cache.get(command.key)
            pipe_get.send(v if v!=None else 0)
        if command.type == -1:
            return



class Command(object):
    def __init__(self, type, key, value=None):
        self.type = int(type)
        self.key = key
        self.value = value
