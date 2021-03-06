from array import array as C_Array
from LinkedListArrays import getNext, getPrev, getHead, getTail, increment, switch, pop, push, bringToFirst, setIndex
from threading import Lock


class CacheSlubLRU(object):

    def __init__(self, totalSize, slabSize, logger):
        # to create slabArray:
        #before self.slabArray = C_Array('c', '0'*self.totalSize)
        #now self.slabArray.fromString('0'*slabSize)
        # to create '0'*totalSize string, system will use double of ram. with incremental appending, ram is not overloaded during initialization

        self.logger = logger

        self.logger.debug("Cache: Initializing cache with totalSize:" + str(totalSize/1000000.0) + "MB, slabSize:" + str(slabSize/1000000.0)+"MB")

        self.slabSize = slabSize
        self.totalSize = totalSize

        self.slabNumber = int(self.totalSize / self.slabSize)

        self.slabArray = C_Array('c')
        i=0
        ar = self.slabArray
        while i < self.slabNumber:
            ar.fromstring("0"*slabSize)
            i += 1

        #lru linked list

        self.taglru = 0
        self.tagunused = 1
        self.tagpartial = 2
        self.tagcomplete = 3
        self.llheads  = [None, None, None, None]
        self.lltails = [None, None, None, None]
        self.lllen = [0, 0, 0, 0]
        self.lrumutex = Lock()
        #
        self.cache = {}#collections.defaultdict() #dictionary of key-slab

        self.purged = 0

        for slabIndex in xrange(self.slabNumber):
            slab = Slab(self, slabIndex,self.slabSize, self.slabNumber, self.totalSize)

            push(self,self.taglru, slab)
            push(self, self.tagunused, slab)

        self.logger.debug("Cache: End of Initialization Cache, Success!")






    def getSlab(self, size):

        slab = getHead(self, self.tagpartial)

        while (slab != None):
            if slab.availableSpace >= size:
                return slab
            slab = getNext(self.tagpartial, slab)


        # no partial compatible slabs
        if getHead(self, self.tagunused) != None:
            # print "new unused slab requested"
            #return an unused slab
            slab = getHead(self, self.tagunused)

            #it's a new slab, it must not be purged soon
            self.lrumutex.acquire()
            bringToFirst(self,self.taglru, slab)
            self.lrumutex.release()
            return slab

        else:
            return self.purgeLRUSlab()

    # purge an entire slab, move it from complete/partial to unused
    def purgeLRUSlab(self):
        #activate lru purge
        self.purged += 1
        #print "slab purged"
        #get the last slab in lru list
        self.lrumutex.acquire()
        slab = getTail(self,self.taglru)
        bringToFirst(self, self.taglru,slab)
        self.lrumutex.release()
        #self.logger.debug("Slab purged: "+str(slab))

        if (slab.state == 1):#partial
            pop(self, self.tagpartial, slab)
        if (slab.state == 2):#complete
            pop(self, self.tagcomplete, slab)
        if (slab.state == 0):#unused
            raise Exception("an unused slab is purged, Not possible!")

        slab.clearSlab()
        push(self, self.tagunused, slab)

        return slab


    def set(self, key, value):
        key = int(key)
        if (value == None):
            self.delete(key)
            return None

        valueSize = len(value)
        if valueSize > self.slabSize:
            self.logger.warning("Cache: failed set, too large "+ str(key) + ", value:"+ str(value) + ",size:" + str(valueSize))
            return None

        #self.logger.debug("Cache: set of "+ str(key) + ", value:"+ str(value) + ",size:" + str(valueSize))
        slab = self.cache.get(key)

        if slab!=None:#update existent value
            #self.logger.debug("Cache: set of "+ str(key) + ", it is been updated")

            if slab.hasKey(key): #check if it was purged
                begin, end = slab.value.get(key)

                if valueSize <= end-begin-1: #change

                    slab.updateValue(key, value)
                    self.lrumutex.acquire()
                    increment(self, self.taglru,slab)
                    self.lrumutex.release()

                    slab.value[key] = begin, begin + valueSize
                    return

                else:
                    self.cache[key] = None
                    self.set(key,value)
                    return
            else:
                slab = None # slab was purged. key is still in dictionary but not in slab. it must be created another time
        if slab== None:#insert new element
            #self.logger.debug("Cache: set of "+ str(key) + ", it is been added")
            slab = self.getSlab(valueSize)

            slab.setValue(key, value)
            self.cache[key] = slab

            self.lrumutex.acquire()
            increment(self, self.taglru,slab)
            self.lrumutex.release()

    def delete(self, key):
        key = int(key)
        self.cache.pop(key)

    def get(self, key):
        key = int(key)
        #self.logger.debug("Cache: get of "+ str(key))
        slab = self.cache.get(key)
        if slab != None:
            self.lrumutex.acquire()
            increment(self, self.taglru,slab)
            self.lrumutex.release()

            return slab.getValue(key)
        else:
            return None

    #unused
    def transferMemory(self):
        return getHead(self, self.taglru)


    # this instruction is heavy! Caution
    def debug(self):
        return self.slabArray

class Slab(object):

    def __init__(self, cache, slabIndex,slabSize, slabNumber, totalSize):
        self.slabSize = slabSize
        self.cache = cache
        self.slabIndex = slabIndex
        self.slabArray = cache.slabArray
        self.availableSpace = int(slabSize)  #in bytes
        self.state = 0 #0 unused, 1 partial, 2 complete
        self.value = {} #elements like ("1234", "4", "10") that means, value of key 1234 begins at 4 and ends at 10

        #LL lru cache
        if cache!=None:
            self.nexts = [None, None, None, None]
            self.prevs = [None, None, None, None]
            self.indexes = [None, None, None,None]
            setIndex(self.cache.taglru,self, self.slabIndex)
            setIndex(self.cache.tagunused,self, self.slabIndex)
            setIndex(self.cache.tagpartial,self, self.slabIndex)
            setIndex(self.cache.tagcomplete,self, self.slabIndex)
            #

        self.begin = int( slabIndex * slabSize )
        self.end = int( (slabIndex+1) * slabSize ) -1

    #unused
    def exportSlab(self):
        ex = Slab(None, self.slabIndex, self.slabSize, slabNumber, totalSize)
        ex.state = self.state
        ex.availableSpace = self.availableSpace
        ex.value = self.value.items()

    #unused
    def importSlab(self, ex):
        self.slabIndex = ex.slabIndex
        self.slabNumber =  ex.slabNumber
        self.totalSize =  ex.totalSize
        self.state =  ex.state
        self.availableSpace =  ex.availableSpace
        self.value = dict(ex.value)

    def clearSlab(self):
        self.availableSpace = self.slabSize
        self.value.clear()
        self.state = 0

    def hasKey(self, key):
        return key in self.value

    def getValue(self, key):
        if not key in self.value:
            return None
        begin, end = self.value.get(key)
        value = ""
        if begin == None:
            return None
        for index in xrange(begin,end+1):
            value += self.slabArray[index]

        return value

    def updateValue(self, key, value):
        size = len(value)

        begin, end = self.value[key]
        end = begin + size
        self.value[key] =begin, end
        for index in xrange(begin, end):
            self.slabArray[index]=  value[index-begin]

        if self.availableSpace<=0 and self.state==1:
            self.state = 2
            pop(self.cache, self.cache.tagpartial, self)
            push(self.cache, self.cache.tagcomplete, self)

        return self.state

    def setValue(self, key, value):
        size = len(value)

        begin = self.end - self.availableSpace +1
        end = self.end - self.availableSpace + size

        self.availableSpace -= size

        self.value[key] = begin, end

        for index in xrange(begin, end+1):
            #print begin, index, end
            self.slabArray[index] = value[index-begin]

        if self.state == 0:
            self.state = 1
            pop(self.cache, self.cache.tagunused, self)
            push(self.cache, self.cache.tagpartial, self)

        if self.availableSpace<=0:
            self.state = 2
            pop(self.cache, self.cache.tagpartial, self)
            push(self.cache, self.cache.tagcomplete, self)

        return self.state

    def __str__(self):
        return "index: " + str(self.slabIndex) + "\n"\
        + "slabSize: " +   str(self.slabSize) + "\n"\
        + "availableSpace: " + str(self.availableSpace)  + "\n"\
        + "state: "+ str(self.state)  + "\n"\
        + "dictionary value: " + str(self.value)  + "\n"\
        + "begin: " + str(self.begin)  + "\n"\
        + "end: " + str(self.end)  + "\n"

    def __int__(self):
        return int(self.slabIndex)







#------------------------------------------------Tests----------------------------------------------




def fun(cache, it, getsetratio, valuebytesize):
    import random
    old = 0
    getlist = []

    for i in xrange(it):

        setKey, setValue, getKey = trialPrepare(i ,it,cache, getlist, valuebytesize)


        getratio = 1.0 * getsetratio/ (getsetratio +1)
        setratio = 1.0/ (getsetratio +1)
        if random.random()< getratio:
            trialget(cache, setKey, setValue, getKey)
        else:
            trialset(cache, setKey, setValue, getKey)

        percent = int(i*1.0/it *100)
        if percent%5 == 0 and percent > old:
            old = percent
            print "\b\b\b\b\b"+ str(percent)+"%",

def trialPrepare(i, int,cache, getlist, valuebytesize):
    import random
    integer = random.randint(0,i)
    setValue = "a"*(valuebytesize) #according to facebook article
    setkey = str(random.randint(0,i))
    getlist.append(setkey)
    getkey = random.choice(getlist)
    return setkey, setValue, getkey

def trialset(cache, setKey, setValue, getKey):
    cache.set(setKey, setValue)


def trialget(cache, setKey, setValue, getKey):
    cache.get(getKey)

def trialSplit(cache):
    #LinkedList.printList(cache, "lru")
    import itertools
    n = len(cache.cache) // 2          # length of smaller half
    i = iter(cache.cache.items())      # alternatively, i = d.iteritems() works in Python 2

    d1 = dict(itertools.islice(i, n))   # grab first n items
    d2 = dict(i)                        # grab the rest
    old = 0
    x = 0
    print d1

    for x in cache.cache.items():

        if x[0] < old:
            print old, x[0]
        old = x[0]
    print "-------------------------------------------------------------------------------------------------------"


#Multithread tests


def funWithTask(preallocatedPool, slabSize, it, getsetratio, valuebytesize, getThreadNumber, settings):
    import random
    old = 0
    getlist = []
    from multiprocessing import Process, Pipe

    import logging
    from MemoryManagement import startMemoryTask, Command


    url_getPort = "tcp://localhost:" + str(settings.getMasterGetPort())
    url_setPort = "tcp://localhost:" + str(settings.getMasterSetPort())

    startMemoryTask(settings, logging.getLogger(),True)

    from threading import Thread
    threads = []
    for th in range(0, getThreadNumber):
        t = Process(target=trialThread, args=(it/getThreadNumber, valuebytesize,getsetratio, url_setPort, url_getPort))
        t.start()
        threads.append(t)


    for t in threads:
        t.join()
    for _ in range(settings.getGetterThreadNumber()):
        sendkilltask(url_getPort)
    sendkilltask(url_setPort)
    print "fine"

def trialThread(it, valuebytesize,getsetratio, parent_conn_set, parent_conn_get):
    import random
    print "ciao, sono un thread per richieste per benchmark"
    getlist = []

    for i in xrange(it):

        setKey, setValue, getKey = trialPrepare(i ,it,None,  getlist, valuebytesize)

        getratio = 1.0 * getsetratio/ (getsetratio +1)
        setratio = 1.0/ (getsetratio +1)
        if random.random()< getratio:
            v = sendgettask(setKey, setValue, getKey, parent_conn_get)
            #print "get "+str(getKey)+": " + str(v)
        else:
            sendsettask(setKey, setValue, getKey, parent_conn_set)
            #print "set " + str(setKey) + ": " + str(setValue)


def sendkilltask(parent_conn):

    # killProcess(parent_conn)
    pass

def sendsettask(setKey, setValue, getKey, parent_conn):

    # setRequest(parent_conn, setKey, setValue)
    pass

def sendgettask(setKey, setValue, getKey,parent_conn):

    #    return getRequest(parent_conn, getKey)
    pass

def getSettings(totram, slabSize, getThreadNumber):
    import sys
    sys.path.append("..")
    from Settings import SettingsObject
    return SettingsObject.manualSettings(preallocatedPool=totram, slabSize=slabSize, getterThreadNumber=getThreadNumber, MasterGetPort=5551, MasterSetPort=5550, SlaveGetPort=5553, SlaveSetPort=5552)

def trialGetSet():
    import logging
    import random
    import sys

    kilo = 1000
    mega = 1000 * kilo
    giga = 1000 * mega

    totram = int(sys.argv[1]) if sys.argv[1]!=None  else  10*mega
    slabSize = int(sys.argv[2])if sys.argv[2]!=None else 100*kilo
    it = int(sys.argv[3])if sys.argv[3]!=None else 1000000
    valuebytesize = int(sys.argv[4])if sys.argv[4]!=None else 300
    getsetratio  = int(sys.argv[5])if sys.argv[5]!=None else 5
    getThreadNumber  = int(sys.argv[6])if sys.argv[6]!=None else 6

    settings = getSettings(totram, slabSize, getThreadNumber)

    funWithTask(totram, slabSize, it, getsetratio, valuebytesize, getThreadNumber, settings)

    print "|" + str(it) + "|" + str(getsetratio) + "|" + str(valuebytesize) + "|" + str(totram) + "|" + str(slabSize) + "|"+ str(getThreadNumber)



if __name__ == "__main__":
    trialGetSet()
