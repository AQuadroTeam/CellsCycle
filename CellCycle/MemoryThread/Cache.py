from array import array as C_Array
from sys import getsizeof
from LynkedList import LynkedList
class CacheSlubLRU:

    def __init__(self, totalSize, slabSize):

        self.slabSize = slabSize
        self.totalSize = totalSize


        self.slabArray = C_Array('c','0'*self.totalSize) #empty char array

        self.unused = LynkedList()
        self.partial = LynkedList()
        self.complete = LynkedList()

        self.lru = [] #list of slabs, ordered by last use

        self.cache = {} #dictionary of key-slab

        self.slabNumber = int(self.totalSize / self.slabSize)

        for slabIndex in range(self.slabNumber):
            slab = Slab(self.slabArray, slabIndex,self.slabSize, self.slabNumber, self.totalSize)
            self.lru.append(slab)
            self.unused.append(slab)

    def getSlab(self, size):
        for slab in self.partial:
            if slab.availableSpace >= size:
                return slab
        # no partial compatible slabs
        if self.unused.isEmpty():
            #activate lru purge
            slab = self.lru[len(self.lru)-1]
            if (slab.state == 1):#partial
                self.partial.pop(slab)
                slab.clearSlab()
                self.unused.push(slab)
                return slab
            if (slab.state == 2):#complete
                self.complete.pop(slab)
            if (slab.state == 0):#unused
                self.unused.pop(slab)
            self.updateLRUn(slab,3)

        else:
            #return an unused slab
            slab = self.unused.pop()
            self.updateLRUn(slab,3)
            return slab

    def set(self, key, value):
        valueSize = getsizeof(value)

        slab = self.cache.get(key)

        if slab== None:
            slab = self.getSlab(valueSize)
            slab.addValue(key, value)
            self.updateLru(slab)
        else:
            if less size:
                slab.value[key] = value
            else:
                cache[key] = None

    def get(self, key):
        

    def updateLRU(self, slab):
        index = self.lru.index(slab)
        if index > 0 :
            nextOne = self.lru[index-1]
            self.lru[index] = nextOne
            self.lru[index-1] = slab

    def updateLRUn(self, slab, n):
        for i in range(n):
            self.updateLRU(slab)

class Slab:

    def __init__(self, slabArray, slabIndex,slabSize, slabNumber, totalSize):
        self.slabSize = slabSize
        self.slabArray = slabArray
        self.availableSpace = int(slabSize)  #in bytes
        self.state = 0 #0 unused, 1 partial, 2 complete
        self.value = {} #elements like ("1234", "4", "10") that means, value of key 1234 begins at 4 and ends at 10

        self.begin = int( slabIndex * slabSize )
        self.end = int( (slabIndex+1) * slabSize ) -1

    def clearSlab(self):
        self.availableSpace = self.slabSize
        self.value.clear()
        self.state = 0
