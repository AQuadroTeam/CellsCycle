#! /usr/bin/env python


class ChainList:

    def __init__(self):
        self.dictionary = dict()

    def add_node(self, target_node, target_master, target_slave):
        list_key = ListKey(target_node.id)
        list_value = ListValue(target_node)
        list_value.add_master(target_master)
        list_value.add_slave(target_slave)
        self.dictionary[list_key.key] = list_value

    def remove_node(self, target_id):
        try:
            del(self.dictionary[target_id])
        except KeyError:
            raise KeyError

    # Search for a memory key in list, returns None if key_to_find is not part of the dictionary
    # def find_memory_key(self, key_to_find):
    #     for k, v in self.dictionary.iteritems():
    #         if int(v.master.min_key) <= key_to_find <= int(v.master.max_key) or\
    #            int(v.slave.min_key) <= key_to_find <= int(v.slave.max_key):
    #             return v
    #     return None
    def find_memory_key(self, key_to_find):
        for v in self.dictionary.itervalues():
            if int(v.target.min_key) > int(v.target.max_key):
                min_key = int(v.target.min_key)
                max_key = int(v.target.max_key)
                first_test = min_key <= key_to_find < float("inf")
                second_test = 0 <= key_to_find <= max_key
                # This is the case in which we close the cycle
                if first_test or second_test:
                    return v
            else:
                if int(v.target.min_key) <= key_to_find <= int(v.target.max_key):
                    return v
        return None

    # Returns a value with a key as parameter
    def get_value(self, key):
        try:
            return self.dictionary[key]
        except KeyError:
            raise KeyError

    # Is this id in list
    def is_in_list(self, key):
        return key in self.dictionary

    def print_list(self):
        return ''.join('Node {}, {}\n'.format(key, val.print_value()) for key, val in self.dictionary.items())


class ListKey:

    def __init__(self, target_key):
        self.key = target_key


class ListValue:

    def __init__(self, target):
        self.target = target
        self.master = None
        self.slave = None

    def add_master(self, target):
        self.master = target

    def add_slave(self, target):
        self.slave = target

    def print_value(self):
        # return ''.join('Node :\n {}\n'.format(u) for u in [self.target.id, self.master.id,
        #                                                    self.slave.id])
        # if self.slave is None:
        #     slave_to_print = 'None'
        # else:
        #     slave_to_print = self.slave.id
        # if self.master is None:
        #     master_to_print = 'None'
        # else:
        #     master_to_print = self.master.id

        # target_to_print = self.target.print_values()
        # master_to_print = self.master.print_values()
        # slave_to_print = self.slave.print_values()
        target_to_print = self.target.id
        master_to_print = self.master.id
        slave_to_print = self.slave.id

        return 'Node : myself {}, master {}, slave {}\n'.format(target_to_print, master_to_print, slave_to_print)
        # return 'Node : myself {}, master {}, slave {}\n'.format(target_to_print, master_to_print, slave_to_print)


