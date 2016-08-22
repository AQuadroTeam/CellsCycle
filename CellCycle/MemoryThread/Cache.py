from array import array as C_Array
from sys import getsizeof
from LinkedList import LinkedList
class CacheSlubLRU:

    def __init__(self, totalSize, slabSize, logger):
        # to create slabArray:
        #before self.slabArray = C_Array('c', '0'*self.totalSize)
        #now self.slabArray.fromString('0'*slabSize)
        # to create '0'*totalSize string, system will use double of ram. with incremental appending, ram is not overloaded during initialization

        self.logger = logger
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

        self.lru = [] #list of slabs, ordered by last use

        self.cache = {} #dictionary of key-slab



        for slabIndex in range(self.slabNumber):
            slab = Slab(self, slabIndex,self.slabSize, self.slabNumber, self.totalSize)
            self.lru.append(slab)
            self.unused.append(slab)



    def getSlab(self, size):
        for slab in self.partial:
            if slab.availableSpace >= size:
                return slab


        # no partial compatible slabs
        if len(self.unused)<1:
            #activate lru purge
            slab = self.lru[len(self.lru)-1]
            if (slab.state == 1):#partial
                self.partial.remove(slab)
            if (slab.state == 2):#complete
                self.complete.remove(slab)
            if (slab.state == 0):#unused
                self.unused.remove(slab)
            slab.clearSlab()
            self.unused.append(slab)
            self.updateLRUn(slab,3)
            return slab

        else:
            #return an unused slab
            slab = self.unused[-1]
            self.updateLRUn(slab,3)
            return slab

    def set(self, key, value):
        valueSize = len(value)

        slab = self.cache.get(key)

        if slab== None:#insert new element
            slab = self.getSlab(valueSize)
            slab.setValue(key, value)
            self.cache[key] = slab
            self.updateLRU(slab)
        else:#update existent value
            if False: #change
                slab.setValue(key, value)
                self.updateLRU(slab)

            else:
                self.cache[key] = None
                self.set(key,value)

    def get(self, key):
        slab = self.cache.get(key)
        self.updateLRU(slab)
        return slab.getValue(key)

    def updateLRU(self, slab):
        index = self.lru.index(slab)
        if index > 0 :
            nextOne = self.lru[index-1]
            self.lru[index] = nextOne
            self.lru[index-1] = slab

    def updateLRUn(self, slab, n):
        for i in range(n):
            self.updateLRU(slab)

    def debug(self):
        return self.slabArray

class Slab:

    def __init__(self, cache, slabIndex,slabSize, slabNumber, totalSize):
        self.slabSize = slabSize
        self.cache = cache
        self.slabArray = cache.slabArray
        self.availableSpace = int(slabSize)  #in bytes
        self.state = 0 #0 unused, 1 partial, 2 complete
        self.value = {} #elements like ("1234", "4", "10") that means, value of key 1234 begins at 4 and ends at 10

        self.begin = int( slabIndex * slabSize )
        self.end = int( (slabIndex+1) * slabSize ) -1

    def clearSlab(self):
        self.availableSpace = self.slabSize
        self.value.clear()
        self.state = 0
        print self.availableSpace, self.slabSize

    def getValue(self, key):
        begin, end = self.value[key]
        value = ""
        for index in range(begin,end+1):
            value += self.slabArray[index]

        return value

    def setValue(self, key, value):
        size = len(value)



        begin = self.end - self.availableSpace +1
        print self.end, self.availableSpace
        end = self.end - self.availableSpace + size

        self.availableSpace -= size

        self.value[key] = begin, end

        for index in range(begin, end+1):
            print begin, end, index
            print self.slabArray
            print value[index-begin]
            self.slabArray[index] = value[index-begin]

        if self.state == 0:
            for x in self.cache.unused:
                print x
            self.state = 1
            self.cache.unused.remove(self)
            self.cache.partial.append(self)

        if self.availableSpace<=1000:
            self.state = 2
            self.cache.partial.remove(self)
            self.cache.complete.append(self)

        return self.state

    def __str__(self):
        return "slabSize: " +   str(self.slabSize) + "\n"\
        + "availableSpace: " + str(self.availableSpace)  + "\n"\
        + "state: "+ str(self.state)  + "\n"\
        + "dictionary value: " + str(self.value)  + "\n"\
        + "begin: " + str(self.begin)  + "\n"\
        + "end: " + str(self.end)  + "\n"
