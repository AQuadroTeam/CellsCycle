#! /usr/bin/env python

from ListThread import ListThread
from ListCommunication import ListCommunication
from zmq import Again
from ProdCons import ProducerThread
from random import randint
# from Queue import Queue

FILE_PATH = './my_list'
DEAD = 'DEAD'
PRIORITY_DEAD = '3'
PRIORITY_ALIVE = '0'
PRIORITY_ADD = '2'
DEFAULT_ADDR = '127.0.0.1'
CHILD_SYNC = "CHILD SYNC"
TXT = '.txt'
DEF_NODES = 3
BUF_SIZE = 10
SECRETARY_PORT = '5186'

class Generator(ProducerThread):
    def __init__(self, threadId, prevId, slave, slave_of_slave, masterMemory, slaveMemory, logger, condition, delay):
        ProducerThread.__init__(self, threadId, prevId, slave, slave_of_slave, masterMemory, slaveMemory, logger, condition, delay)
        self.logger.debug("These are my features (Reader): (" + self.myself + ") Master ID : " + self.masterId + " SlaveID: " + self.slaveId)

    def run(self):
        # time.sleep(int(self.myself))
        print "Starting Reader " + self.myself
        self.generate(self.myself, 2)
        print "Exiting Reader " + self.myself

    def initReqRepConnection(self):
        listCommunication = ListCommunication(DEFAULT_ADDR,SECRETARY_PORT)
        listCommunication.open_rep_socket()
        try:
            listCommunication.sync()
        except Again:
            raise Again
        return listCommunication

    def generate(self, threadName, counter):

        try:
            listCommunication = self.initReqRepConnection()
        except Again:
            self.logger.debug("No answers from the new node, i\'m " + self.myself)
            return

        self.logger.debug("Node added i\'m " + self.myself)
        self.produce(CHILD_SYNC)

if __name__ == '__main__':
    # Create new threads
    thread2 = Generator([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = Generator([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"
