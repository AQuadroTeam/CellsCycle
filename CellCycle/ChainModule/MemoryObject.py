# This is the object passed to Memory Module


class MemoryObject:

    def __init__(self, master_of_master, master, myself, slave, slave_of_slave):
        self.master_of_master = master_of_master
        self.master = master
        self.myself = myself
        self.slave = slave
        self.slave_of_slave = slave_of_slave
