from Cache import Slab, CacheSlubLRU

def startMemoryThread(settings, logger):

    logger.debug("Hello, I'm a funny thread")
    logger.debug(settings)

    kilo = 1000
    mega = 1000 * kilo
    giga = 1000 * mega
    cache = CacheSlubLRU(100 , 10, logger) #set as 10 mega, 1 mega per slab


    for i in range(10000):
        cache.set(str(i), "val"+str(i))
        print cache.debug()
