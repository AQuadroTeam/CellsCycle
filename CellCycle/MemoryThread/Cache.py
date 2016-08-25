from array import array as C_Array
from sys import getsizeof
import LinkedListArrays as LinkedList


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

        #
        self.cache = {}#collections.defaultdict() #dictionary of key-slab

        self.purged = 0

        for slabIndex in xrange(self.slabNumber):
            slab = Slab(self, slabIndex,self.slabSize, self.slabNumber, self.totalSize)

            LinkedList.push(self,self.taglru, slab)
            LinkedList.push(self, self.tagunused, slab)

        self.logger.debug("Cache: End of Initialization Cache, Success!")

    def getSlab(self, size):

        slab = LinkedList.getHead(self, self.tagpartial)

        while (slab != None):
            if slab.availableSpace >= size:
                return slab
            slab = LinkedList.getNext(self.tagpartial, slab)


        # no partial compatible slabs
        if LinkedList.getHead(self, self.tagunused) != None:
            # print "new unused slab requested"
            #return an unused slab
            slab = LinkedList.getHead(self, self.tagunused)

            #it's a new slab, it must not be purged soon
            LinkedList.bringToFirst(self,self.taglru, slab)

            return slab

        else:
            return self.purgeLRUSlab()

    def purgeLRUSlab(self):
        #activate lru purge
        self.purged += 1
        print "slab purged"
        #get the last slab in lru list
        slab = LinkedList.getTail(self,self.taglru)
        if (slab.state == 1):#partial
            LinkedList.pop(self, self.tagpartial, slab)
        if (slab.state == 2):#complete
            LinkedList.pop(self, self.tagcomplete, slab)
        if (slab.state == 0):#unused
            raise Exception("an unused slab is purged, Not possible!")

        slab.clearSlab()
        LinkedList.push(self, self.tagunused, slab)

        LinkedList.bringToFirst(self, self.taglru,slab)
        return slab


    def set(self, key, value):
        key = int(key)

        valueSize = len(value)
        if valueSize > self.slabSize:
            self.logger.warning("Cache: failed set, too large "+ str(key) + ", value:"+ str(value) + ",size:" + str(valueSize))
            return None

        #self.logger.debug("Cache: set of "+ str(key) + ", value:"+ str(value) + ",size:" + str(valueSize))
        slab = self.cache.get(key)

        if slab== None:#insert new element
            #self.logger.debug("Cache: set of "+ str(key) + ", it is been added")
            slab = self.getSlab(valueSize)

            slab.setValue(key, value)
            self.cache[key] = slab
            LinkedList.increment(self, self.taglru,slab)

        else:#update existent value
            #self.logger.debug("Cache: set of "+ str(key) + ", it is been updated")
            if not key in slab.value:
                return None
            begin, end = slab.value.get(key)

            if valueSize <= end-begin-1: #change

                slab.updateValue(key, value)
                LinkedList.increment(self, self.taglru,slab)
                slab.value[key] = begin, begin + valueSize

            else:
                self.cache[key] = None
                self.set(key,value)

    def get(self, key):
        key = int(key)
        #self.logger.debug("Cache: get of "+ str(key))
        slab = self.cache.get(key)
        if slab != None:
            LinkedList.increment(self, self.taglru,slab)
            return slab.getValue(key)
        else:
            return None

    #def updateLRU(self, slab):
    #    index = self.lru.index(slab) # rhis istruction is heavy
    #    if index > 0 :
    #        nextOne = self.lru[index-1]
    #        self.lru[index] = nextOne
    #        self.lru[index-1] = slab

    #def updateLRUn(self, slab, n):
    #    for i in xrange(n):
    #        self.updateLRU(slab)

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

        self.nexts = [None, None, None, None]
        self.prevs = [None, None, None, None]
        self.indexes = [None, None, None,None]
        LinkedList.setIndex(self.cache.taglru,self, self.slabIndex)
        LinkedList.setIndex(self.cache.tagunused,self, self.slabIndex)
        LinkedList.setIndex(self.cache.tagpartial,self, self.slabIndex)
        LinkedList.setIndex(self.cache.tagcomplete,self, self.slabIndex)
        #

        self.begin = int( slabIndex * slabSize )
        self.end = int( (slabIndex+1) * slabSize ) -1

    def clearSlab(self):
        self.availableSpace = self.slabSize
        self.value.clear()
        self.state = 0

        for i in xrange(self.begin, self.end+1):
            self.slabArray[i] = "0"

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
            LinkedList.pop(self.cache, self.cache.tagpartial, self)
            LinkedList.push(self.cache, self.cache.tagcomplete, self)

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
            LinkedList.pop(self.cache, self.cache.tagunused, self)
            LinkedList.push(self.cache, self.cache.tagpartial, self)

        if self.availableSpace<=0:
            self.state = 2
            LinkedList.pop(self.cache, self.cache.tagpartial, self)
            LinkedList.push(self.cache, self.cache.tagcomplete, self)

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

    cache = CacheSlubLRU(totram , slabSize,logging.getLogger())
    #cache = CacheSlubLRU(100, 10, logging.getLogger())
    fun(cache, it, getsetratio, valuebytesize)

    print "|" + str(it) + "|" + str(getsetratio) + "|" + str(valuebytesize) + "|" + str(totram) + "|" + str(slabSize) + "|" + str(cache.purged) + "|"



if __name__ == "__main__":
    trialGetSet()
