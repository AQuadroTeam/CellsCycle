# This is the object passed to Memory Module


class MemoryObject:

    def __init__(self, master_of_master, master, myself, slave, slave_of_slave):
        self.master_of_master = master_of_master
        self.master = master
        self.myself = myself
        self.slave = slave
        self.slave_of_slave = slave_of_slave

    def __str__(self):
        rel = [self.myself, self.master, self.master_of_master, self.slave, self.slave_of_slave]
        to_print = ["myself", "master", "master_of_master", "slave", "slave_of_slave"]
        str_to_print = ''
        for x in xrange(len(rel)):
            key = to_print[x]
            val = rel[x]
            str_to_print += 'Node {}, id {}, keys {}\n'.format(key, val.id, val.get_min_max_key())
        return str_to_print

    def print_elements(self):
        rel = [self.myself, self.master, self.master_of_master, self.slave, self.slave_of_slave]
        to_print = ["myself", "master", "master_of_master", "slave", "slave_of_slave"]
        str_to_print = ''
        for x in xrange(len(rel)):
            key = to_print[x]
            val = rel[x]
            str_to_print += 'Node {}, id {}, keys {}\n'.format(key, val.id, val.get_min_max_key())
        return str_to_print
