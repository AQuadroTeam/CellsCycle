from Cache import Slab, CacheSlubLRU

def startMemoryThread(settings, logger):

    logger.debug("Hello, I'm a funny thread")
    logger.debug(settings)

    logger.debug("Initializing object pool...")
    cache = CacheSlubLRU(100 , 10, logger) #set as 10 mega, 1 mega per slab
    logger.debug("Initializing object pool... done")

    for slab in cache.lru:
        print slab
    cache.set("1", "valore")
    print cache.debug()
    for slab in cache.lru:
        print slab

    cache.set("2", "cia")
    print cache.debug()
    for slab in cache.lru:
        print slab

    print "a" + 2
    cache.set("3", "ciaone2")
    print cache.debug()
    for slab in cache.lru:
        print slab


    cache.set("3", "ciaone3")
    print cache.debug()
    for slab in cache.lru:
        print slab


    cache.set("4", "ciaone4")
    print cache.debug()
    for slab in cache.lru:
        print slab


    cache.set("5", "ciaone5")
    print cache.debug()
    for slab in cache.lru:
        print slab


    cache.set("6", "ciaone6")
    print cache.debug()
    for slab in cache.lru:
        print slab


    cache.set("7", "ciaone7")
    print cache.debug()
    for slab in cache.lru:
        print slab



    cache.set("8", "ciaone8")
    print cache.debug()
    for slab in cache.lru:
        print slab


    cache.set("9", "ciaone9")
    print cache.debug()
    for slab in cache.lru:
        print slab



    cache.set("10", "ciaone10")
    print cache.debug()
    for slab in cache.lru:
        print slab

    print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    print "v: " + cache.get("4")
