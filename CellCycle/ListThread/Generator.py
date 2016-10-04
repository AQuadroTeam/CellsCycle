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
TXT = '.txt'
DEF_NODES = 3
BUF_SIZE = 10

class Generator(ProducerThread):
    def __init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay):
        ProducerThread.__init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay)
        self.logger.debug("These are my features (Reader): (" + self.threadId + ") Master ID : " + self.masterId + " SlaveID: " + self.slaveId)

    def run(self):
        # time.sleep(int(self.threadId))
        print "Starting Reader " + self.threadId
        self.generate(self.threadId, 2)
        print "Exiting Reader " + self.threadId

    def initReqRepConnection(self):
        # Troppo hardcoded
        listCommunication = ListCommunication(DEFAULT_ADDR,'5186')
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
            self.logger.debug("No answers from the new node, i\'m " + self.threadId)
            return

        self.logger.debug("Node added i\'m " + self.threadId)
        self.produce("CHILD SYNC")

if __name__ == '__main__':
    # Create new threads
    thread2 = Generator([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = Generator([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"
