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
    while True:
        getCommand = getQueue.get()
        cache.get(getCommand)
        i+=1

def memoryThreadSetter(cache, setQueue):
    i = 0
    while True:
        setCommand = setQueue.get()
        cache.set(setCommand[0], setCommand[1])
        i+=1
