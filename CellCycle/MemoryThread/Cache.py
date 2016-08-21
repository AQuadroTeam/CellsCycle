import array

class CacheSlubLRU:
    
    def __init__(self, totalSize, slabSize):

        self.slabSize = slabSize
        self.totalSize = totalSize


        self.slabArray = array.array('c','0'*self.totalSize) #empty char array

        self.unused = []
        self.partial = []
        self.complete = []

        self.lru = [] #list of slabs, ordered by last use

        self.cache = {} #dictionary of key-slab

        self.slabNumber = int(self.totalSize / self.slabSize)

        for slabIndex in range(self.slabNumber):
            slab = Slab(slabIndex,self.slabSize, self.slabNumber, self.totalSize)
            self.lru.append(slab)
            self.unused.append(slab)

        print "done"
class Slab:

    def __init__(self, slabIndex,slabSize, slabNumber, totalSize):

        self.availableSpace = int(slabSize)  #in bytes
        self.state = 0 #0 unused, 1 partial, 2 complete
        self.value = {} #elements like ("1234", "4", "10") that means, value of key 1234 begins at 4 and ends at 10

        self.begin = int( slabIndex * slabSize )
        self.end = int( (slabIndex+1) * slabSize ) -1

if __name__ =="__main__":
    cache = CacheSlubLRU(12000000000 , 1000000)
