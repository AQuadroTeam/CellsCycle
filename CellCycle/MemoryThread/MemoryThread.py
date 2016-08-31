from Cache import Slab, CacheSlubLRU
import Queue
from multiprocessing import Process, Pipe

def startMemoryThread(settings, logger):
    parent_conn, child_conn = Pipe()
    p = Process(target=startMemoryTask, args=(settings, logger, child_conn))

    for i in range(0,10):
        parent_conn.send(Command(0, "chiave", "valore"))
    print "input pronto, il task nasce"
    p.start()
    print "aspetto il task"
    p.join()
    print "e' morto il task"

def startMemoryTask(settings, logger, pipe):

    logger.debug("Hello, I'm a funny thread")
    logger.debug(settings)


    preallocatedPool= settings.getPreallocatedPool()
    slabSize = settings.getSlabSize()

    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab

    i = 0
    while i < 50:
        command = pipe.recv()
        print command.key, command.value
        i += 1

class Command(object):
    def __init__(self, type, key, value=None):
        self.type = int(type)
        self.key = key
        self.value = value


def memoryThreadGetter(cache, getQueue):
    i = 0
    cache.ready.acquire()
    cache.ready.wait()
    cache.ready.release()
    while getQueue.qsize()>0:
        getCommand = getQueue.get()
        cache.get(getCommand)
        i+=1
        getQueue.task_done()

def memoryThreadSetter(cache, setQueue):
    i = 0
    cache.ready.acquire()
    cache.ready.wait()
    cache.ready.release()
    while setQueue.qsize()>0:
        setCommand = setQueue.get()
        cache.set(setCommand[0], setCommand[1])
        i+=1
        setQueue.task_done()
