from Cache import Slab, CacheSlubLRU


def startMemoryThread(settings, logger):

    logger.debug("Hello, I'm a funny thread")
    logger.debug(settings)


    preallocatedPool= settings.getPreallocatedPool()
    slabSize = settings.getSlabSize()



    cache = CacheSlubLRU(preallocatedPool , slabSize, logger) #set as 10 mega, 1 mega per slab


    for i in range(10000):
        cache.set(str(i), "val"+str(i))
    
