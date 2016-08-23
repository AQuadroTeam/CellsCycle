from array import array as C_Array
from sys import getsizeof
import LinkedList


class CacheSlubLRU:

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

        self.unused = []
        self.partial = []
        self.complete = []

        #lru linked list
        self.llhead = None
        self.lltail = None
        #

        self.cache = {} #dictionary of key-slab



        for slabIndex in xrange(self.slabNumber):
            slab = Slab(self, slabIndex,self.slabSize, self.slabNumber, self.totalSize)

            LinkedList.push(self, slab)

            self.unused.append(slab)

        self.logger.debug("Cache: End of Initialization Cache, Success!")

    def getSlab(self, size):

        for slab in self.partial:
            if slab.availableSpace >= size:
                return slab


        # no partial compatible slabs
        if len(self.unused)>=1:
            print "new slab requested"
            #return an unused slab
            slab = self.unused[-1]

            #it's a new slab, it must not be purged soon
            LinkedList.bringToFirst(self, slab)

            return slab

        else:
            return self.purgeLRUSlab()

    def purgeLRUSlab(self):
        #activate lru purge
        print "slab purged"
        #get the last slab in lru list
        slab = LinkedList.getTail(self)
        if (slab.state == 1):#partial
            self.partial.remove(slab)
        if (slab.state == 2):#complete
            self.complete.remove(slab)
        if (slab.state == 0):#unused
            raise Exception("an unused slab is purged, Not possible!")

        slab.clearSlab()
        self.unused.append(slab)

        LinkedList.bringToFirst(self, slab)
        return slab


    def set(self, key, value):
        valueSize = len(value)
        if valueSize > self.slabSize:
            self.logger.warning("Cache: failed set, too large "+ str(key) + ", value:"+ str(value) + ",size:" + str(valueSize))
            return None

        self.logger.debug("Cache: set of "+ str(key) + ", value:"+ str(value) + ",size:" + str(valueSize))
        slab = self.cache.get(key)

        if slab== None:#insert new element
            self.logger.debug("Cache: set of "+ str(key) + ", it is been added")
            slab = self.getSlab(valueSize)

            slab.setValue(key, value)
            self.cache[key] = slab
            LinkedList.increment(self, slab)

        else:#update existent value
            self.logger.debug("Cache: set of "+ str(key) + ", it is been updated")
            if not key in slab.value:
                return None
            begin, end = slab.value.get(key)

            if valueSize <= end-begin-1: #change

                slab.updateValue(key, value)
                LinkedList.increment(self, slab)
                slab.value[key] = begin, begin + valueSize

            else:
                self.cache[key] = None
                self.set(key,value)

    def get(self, key):
        self.logger.debug("Cache: get of "+ str(key))
        slab = self.cache.get(key)
        if slab != None:
            LinkedList.increment(self, slab)
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

class Slab:

    def __init__(self, cache, slabIndex,slabSize, slabNumber, totalSize):
        self.slabSize = slabSize
        self.cache = cache
        self.slabIndex = slabIndex
        self.slabArray = cache.slabArray
        self.availableSpace = int(slabSize)  #in bytes
        self.state = 0 #0 unused, 1 partial, 2 complete
        self.value = {} #elements like ("1234", "4", "10") that means, value of key 1234 begins at 4 and ends at 10

        #LL lru cache
        self.llprev = None
        self.llnext = None
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
            self.cache.partial.remove(self)
            self.cache.complete.append(self)

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
            self.cache.unused.remove(self)
            self.cache.partial.append(self)

        if self.availableSpace<=0:
            self.state = 2
            self.cache.partial.remove(self)
            self.cache.complete.append(self)

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

def fun(cache, it):
    import random
    for i in xrange(it):
        integer = random.randint(0,i)

        cache.set(str(random.randint(0,i)), str(i)*(100))
        cache.get(str(integer))
        print "\b\b\b\b\b\b\b\b\b"+ str(i*1.0/it *100)+"%",

def trialLinkedList():
    import logging
    kilo = 1000
    mega = 1000 * kilo
    giga = 1000 * mega

    cache = CacheSlubLRU(100*kilo , 1*kilo,logging.getLogger()) #set as 10 mega, 1 mega per slab
    #cache = CacheSlubLRU(100, 10, logging.getLogger())
    it  = 100000
    fun(cache, it)
    LinkedList.printList(cache)





    #for x in cache.lru:
    #    print x

if __name__ == "__main__":
    trialLinkedList()
