from Cache import Slab, CacheSlubLRU
import Queue
from multiprocessing import Process, Pipe

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

def startMemoryTask(preallocatedPool, slabSize, logger, pipe):

    logger.debug("Hello, I'm a funny thread")


    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab
    pipe.send(None)

    while True:
        command = pipe.recv()
        if command.type == 0:
            cache.set(command.key, command.value)
        if command.type == 1:
            pipe.send(cache.get(command.key))
        if command.type == -1:
            return



class Command(object):
    def __init__(self, type, key, value=None):
        self.type = int(type)
        self.key = key
        self.value = value
