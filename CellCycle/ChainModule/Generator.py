#! /usr/bin/env python

from ListThread import Node
from DeadReader import DeadReader
from DeadWriter import DeadWriter
from json import loads

MYSELF = 'myself'
MASTER = 'master'
SLAVE = 'slave'
MASTER_OF_MASTER = 'master_of_master'
SLAVE_OF_SLAVE = 'slave_of_slave'

ID = 'id'
IP = 'ip'
MIN_KEY = 'min_key'
MAX_KEY = 'max_key'

# unused
# def get_args():
#     parser = ArgumentParser(description='Process Cells Cycle')
#     parser.add_argument('myself', type=list, help='the node we are talking about')
#     parser.add_argument('master', type=list, help='the node\'s master')
#     parser.add_argument('slave', type=list, help='the node\'s slave')
#     parser.add_argument('master_of_master', type=list, help='the node\'s master of master')
#     parser.add_argument('slave_of_slave', type=list, help='the node\'s slave of slave')

#     return parser.parse_args()


class Generator:
    def __init__(self, logger, settings, json_arg):
        self.logger = logger
        self.settings = settings
        self.args = loads(json_arg)

    def get_node_from_data(self, data):
        return Node(data[ID], data[IP], self.settings.getIntPort(),
                    self.settings.getExtPort(), min_key=data[MIN_KEY], max_key=data[MAX_KEY])

    def create_process_environment(self):
        myself = self.args[MYSELF]
        myself = self.get_node_from_data(myself)
        master = self.args[MASTER]
        master = self.get_node_from_data(master)
        slave = self.args[SLAVE]
        slave = self.get_node_from_data(slave)
        master_of_master = self.args[MASTER_OF_MASTER]
        master_of_master = self.get_node_from_data(master_of_master)
        slave_of_slave = self.args[SLAVE_OF_SLAVE]
        slave_of_slave = self.get_node_from_data(slave_of_slave)

        reader = DeadReader(myself, master, slave, slave_of_slave, master_of_master, self.logger, self.settings)
        writer = DeadWriter(myself, master, slave, slave_of_slave, master_of_master, self.logger, self.settings)

        reader.run()
        writer.run()

    # unused
    # def create_process(self):
    #     Process(name='ListCommunicationProcess', target=Generator._create_process_environment(self))


class Parameter:    # unused

    def __init__(self, myself, master, slave, master_of_master, slave_of_slave):
        self.myself = myself
        self.slave = slave
        self.slave_of_slave = slave_of_slave
        self.master = master
        self.master_of_master = master_of_master

