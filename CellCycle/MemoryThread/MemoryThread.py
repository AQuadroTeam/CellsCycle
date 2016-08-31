from Cache import Slab, CacheSlubLRU
import Queue

def startMemoryThread(settings, logger):

    logger.debug("Hello, I'm a funny thread")
    logger.debug(settings)


    preallocatedPool= settings.getPreallocatedPool()
    slabSize = settings.getSlabSize()

    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab


    for i in range(10000):
        cache.set(str(i), "val"+str(i))



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
