#! /usr/bin/env python

from ProdCons import ProducerThread
from ListCommunication import ListCommunication
from zmq import Again
from random import randint

FILE_PATH = './my_list'
DEAD = 'DEAD'
PRIORITY_DEAD = '3'
PRIORITY_ADD = '2'
PRIORITY_REMOVE = '1'
PRIORITY_ALIVE = '0'
DEFAULT_ADDR = '127.0.0.1'
TXT = '.txt'
DEF_NODES = 3
BUF_SIZE = 10

class DeadReader(ProducerThread):
    def __init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay):
        ProducerThread.__init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay)
        self.logger.debug("These are my features (Reader): (" + self.threadId + ") Master ID : " + self.masterId + " SlaveID: " + self.slaveId)
        self.dead_message = ''
        self.last_version = 1

    def run(self):
        print "Starting Reader " + self.threadId
        self.processRequest(self.threadId)
        print "Exiting Reader " + self.threadId

    def initConnection(self):
        # We have to subscribe to our master
        listCommunication = ListCommunication(DEFAULT_ADDR,self.masterAddr)
        listCommunication.initServerSocket()
        self.logger.debug('Sync completed. New client socket (Writer ' + self.threadId + ') to node ' + self.slaveId + ' with address ' + listCommunication.completeAddress)
        return listCommunication

    def processRequest(self, threadName):

        listCommunication = self.initConnection()

        while True:
        # for i in xrange(2):

            # do your own job

            self.logger.debug('I\'m worker ' + self.threadId + ' and this throughput is too much : ' + str(randint(1000,9999)))
            self.add_message = str(self.last_version) + ' ' + PRIORITY_ADD + ' ' + str(randint(1000,9999)) + ' ' + self.masterId + ' ' + self.threadId

            self.produce(self.add_message)
            self.logger.debug("This is my add_message (" + self.threadId + ") : " + self.add_message)
            self.last_version += 1

            # crea thread che aspetta il nuovo tizio





if __name__ == '__main__':
    # Create new threads
    thread2 = DeadReader([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = DeadReader([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"
