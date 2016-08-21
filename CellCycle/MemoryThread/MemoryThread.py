from Cache import Slab, CacheSlubLRU

def startMemoryThread(settings, logger):

    logger.debug("Hello, I'm a funny thread")
    logger.debug(settings)

    logger.debug("Initializing object pool...")
    cache = CacheSlubLRU(10000000 , 1000000) #set as 10 mega, 1 mega per slab
    logger.debug("Initializing object pool... done")

    import sys,time
    time.sleep(30)
    print "slabArray " +str(sys.getsizeof(cache.slabArray))
    print "unused " + str(sys.getsizeof(cache.unused))
    print "lru " + str(sys.getsizeof(cache.lru))
    print "singleslab" + str(sys.getsizeof(cache.lru[1]))
