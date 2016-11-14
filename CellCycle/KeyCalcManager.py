
def keyCalcToCreateANewNode(oldInfo):
    oldSlave = oldInfo.slave
    oldMyself = oldInfo.myself
    oldMaster = oldInfo.master
    oldSlave_of_slave = oldInfo.slave_of_slave
    oldMaster_of_master = oldInfo.master_of_master

    oldSlavePair = _getPairFromObject(oldSlave)
    oldMyselfPair = _getPairFromObject(oldMyself)
    oldMasterPair = _getPairFromObject(oldMaster)
    oldSlave_of_slavePair = _getPairFromObject(oldSlave_of_slave)
    oldMaster_of_masterPair = _getPairFromObject(oldMaster_of_master)

    newNode = Node(_spliceKeys(oldMyselfPair)[1])
    master = Node(oldMasterPair)
    slave = Node(oldSlavePair)
    myself = Node(_spliceKeys(oldMyselfPair)[0])

    slave_of_slave = Node(oldSlave_of_slavePair)
    master_of_master = Node(oldMaster_of_masterPair)

    return SetOfNodes(myself, master, slave, master_of_master, slave_of_slave, newNode)

def keyCalcWhenMasterDies(oldInfo):
    oldSlave = oldInfo.slave
    oldMyself = oldInfo.myself
    oldMaster = oldInfo.master
    oldSlave_of_slave = oldInfo.slave_of_slave
    oldMaster_of_master = oldInfo.master_of_master

    oldSlavePair = _getPairFromObject(oldSlave)
    oldMyselfPair = _getPairFromObject(oldMyself)
    oldMasterPair = _getPairFromObject(oldMaster)
    oldSlave_of_slavePair = _getPairFromObject(oldSlave_of_slave)
    oldMaster_of_masterPair = _getPairFromObject(oldMaster_of_master)


    master = None
    slave = Node(oldSlavePair)
    myself = Node(_joinKeys(oldMasterPair, oldMyselfPair))

    slave_of_slave = Node(oldSlave_of_slavePair)
    master_of_master = Node(oldMaster_of_masterPair)

    return SetOfNodes(myself, master, slave, master_of_master, slave_of_slave)

def _getPairFromObject(obj):
    return (str(obj.min_key),str(obj.max_key))

def _getObjectFromPair(pair):
    return Node(pair)

def _spliceKeys(pair):
    _min = int(pair[0])
    _max = int(pair[1])

    leng = _max - _min

    firstPair = ( str(_min) , str(_min + int(leng)/2 ))
    secondPair = (str(int(firstPair[1])+1), str(_max))
    return firstPair, secondPair


def _joinKeys(firstPair, secondPair):
    
    return (str(firstPair[0]), str(secondPair[1]))


class Node(object):
    def __init__(self, pair):
        self.min_key = pair[0]
        self.max_key = pair[1]
    def __str__(self):
        return "("+str(self.min_key)+","+str(self.max_key)+")"


class SetOfNodes(object):
    def __init__(self, myself, master, slave, master_of_master, slave_of_slave, newNode=None):
        self.myself = myself
        self.master = master
        self.slave = slave
        self.master_of_master = master_of_master
        self.slave_of_slave = slave_of_slave
        self.newNode = newNode

    def __str__(self):
        return "List of nodes: \n" \
        "master of master : " + str(self.master_of_master) + "\n" \
        "master : " + str(self.master) + "\n" \
        "myself : " + str(self.myself) + "\n" \
        "newNode : " + str(self.newNode) + "\n" \
        "slave : " + str(self.slave) + "\n" \
        "slave of slave : " + str(self.slave_of_slave) + "\n"

    def print_computed_keys(self):
        return ''.join('{}, {}\n'.format(key, str(val)) for key, val in self.__dict__.items())


def tryInput():
    master_of_master = Node((32,63))
    master = Node((64,71))
    myself = Node((72,79))
    slave = Node((80,95))
    slave_of_slave = Node((96,111))

    return SetOfNodes(myself, master, slave, master_of_master, slave_of_slave)


def tryBadInput():
    master_of_master = Node((72,79))
    master = Node((80,95))
    myself = Node((96,111))
    slave = Node((0,32))
    slave_of_slave = Node((33,71))

    return SetOfNodes(myself, master ,slave, master_of_master, slave_of_slave)


def tryBadInput2():
    master_of_master = Node((80,95))
    master = Node((96,111))
    myself = Node((0,32))
    slave = Node((33,71))
    slave_of_slave = Node((72,79))

    return SetOfNodes(myself, master ,slave, master_of_master, slave_of_slave)
