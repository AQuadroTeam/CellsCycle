#! /usr/bin/env python

from multiprocessing import Process
from argparse import ArgumentParser
from ListThread import Node
from DeadReader import DeadReader
from DeadWriter import DeadWriter

ID_INDEX = 0
IP_INDEX = 1
MIN_KEY_INDEX = 2
MAX_KEY_INDEX = 3


def get_args():
    parser = ArgumentParser(description='Process Cells Cycle')
    parser.add_argument('myself', type=list, help='the node we are talking about')
    parser.add_argument('master', type=list, help='the node\'s master')
    parser.add_argument('slave', type=list, help='the node\'s slave')
    parser.add_argument('master_of_master', type=list, help='the node\'s master of master')
    parser.add_argument('slave_of_slave', type=list, help='the node\'s slave of slave')

    return parser.parse_args()


class Generator:
    def __init__(self, logger, settings, args):
        self.logger = logger
        self.settings = settings
        self.args = args

    def _create_process_environment(self):
        myself = self.args.myself
        myself = Node(myself[ID_INDEX], myself[IP_INDEX], self.settings.getIntPort(),
                      self.settings.getExtPort(), min_key=myself[MIN_KEY_INDEX], max_key=myself[MAX_KEY_INDEX])
        master = self.args.master
        master = Node(master[ID_INDEX], master[IP_INDEX], self.settings.getIntPort(),
                      self.settings.getExtPort(), min_key=master[MIN_KEY_INDEX], max_key=master[MAX_KEY_INDEX])
        slave = self.args.slave
        slave = Node(slave[ID_INDEX], slave[IP_INDEX], self.settings.getIntPort(),
                     self.settings.getExtPort(), min_key=slave[MIN_KEY_INDEX], max_key=slave[MAX_KEY_INDEX])
        master_of_master = self.args.master_of_master
        master_of_master = Node(master_of_master[ID_INDEX], master_of_master[IP_INDEX], self.settings.getIntPort(),
                                self.settings.getExtPort(), min_key=master_of_master[MIN_KEY_INDEX],
                                max_key=master_of_master[MAX_KEY_INDEX])
        slave_of_slave = self.args.slave_of_slave
        slave_of_slave = Node(slave_of_slave[ID_INDEX], slave_of_slave[IP_INDEX], self.settings.getIntPort(),
                              self.settings.getExtPort(), min_key=slave_of_slave[MIN_KEY_INDEX],
                              max_key=slave_of_slave[MAX_KEY_INDEX])

        reader = DeadReader(myself, master, slave, slave_of_slave, master_of_master, self.logger, self.settings)
        writer = DeadWriter(myself, master, slave, slave_of_slave, master_of_master, self.logger, self.settings)

        reader.run()
        writer.run()

    def create_process(self):
        Process(name='ListCommunicationProcess', target=Generator._create_process_environment(self))


class Parameter:

    def __init__(self, myself, master, slave, master_of_master, slave_of_slave):
        self.myself = myself
        self.slave = slave
        self.slave_of_slave = slave_of_slave
        self.master = master
        self.master_of_master = master_of_master
