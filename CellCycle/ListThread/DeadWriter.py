#! /usr/bin/env python

# from ListThread import ListThread
import time
from ListCommunication import ListCommunication
from CellCycle.Settings import SettingsManager
from zmq import ZMQError
from random import randint, random
from ProdCons import ConsumerThread
import socket

FILE_PATH = './my_list'
DEAD = 'DEAD'
DEFAULT_ADDR = '127.0.0.1'
TXT = '.txt'
COUNTER = 1
PRIORITY_DEAD = '3'
PRIORITY_ALIVE = '0'
PRIORITY_ADD = '2'
CHILD_SYNC = "CHILD SYNC"


class DeadWriter (ConsumerThread):

    def __init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay):
        ConsumerThread.__init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay)
        self.logger.debug("These are my features (Writer): (" + self.threadId + ") Master ID : " + self.masterId + " SlaveID: " + self.slaveId)
        self.settingsManager = SettingsManager.SettingsManager()
        self.settingsObject = None
        self.version = 1

    def run(self):
        #sleep_index = int(self.threadId) % 3 + 1
        #time.sleep(sleep_index)
        print "Starting Writer " + self.threadId
        self.writeList(self.threadId, COUNTER)
        print "Exiting Writer " + self.threadId

    '''
    With PUB this is a server
    def initConnection(self):
        listCommunication = ListCommunication(DEFAULT_ADDR,self.slaveAddr)
        listCommunication.initClientSocket()
        listCommunication.startClientConnection()
        self.logger.debug('New client socket (Writer ' + self.threadId + ') to node ' + self.slaveId + ' with address ' + listCommunication.completeAddress)
        return listCommunication
    '''
    def writeList(self, threadName, counter):
        '''
        With PUB this is a server
        listCommunication = self.initConnection()
        '''
        listCommunication = ListCommunication(DEFAULT_ADDR,self.threadAddr)
        listCommunication.initServerSocket()

        # just a check for dead nodes
        if self.threadId == '1':
            time.sleep(100000000000000000)

        # Just to give clients some time
        # time.sleep(0.1)

        while True:
            # for i in xrange(2):

            self.logger.debug('Send that i\'m ALIVE (' + self.threadId + ') to ' + self.slaveId)

            # for i in xrange(5):
            try:
                if listCommunication.send(self.threadId + ' ' + PRIORITY_ALIVE) is not None:
                    self.logger.debug('Error sending the message, something went wrong')
            except ZMQError:
                self.logger.debug('Error sending the message, is the server still running?')

            item = self.consume()

            if item is not None:
                self.logger.debug("This is my item (Writer "+ self.threadId + "): " + item)
                # Send the message as a list
                # listCommunication.sendFromFile(FILE_PATH + self.threadId + TXT)
                self.version = max(item[0], self.version)

                if item[2] != PRIORITY_DEAD:
                    if item == CHILD_SYNC:
                       new_node = (int(self.slaveId) - int(self.threadId))/2
                       new_node = str(new_node)
                       # need a little improvement
                       item = str(self.version) + ' ' + PRIORITY_DEAD + ' ' + str(randint(1000,9999)) + ' ' + new_node + ' ' + self.threadId
                       listCommunication.send(item)

                    listCommunication.send(item)
                else:
                    if item[9] == self.slaveId:
                        self.slaveId = self.slaveOfSlaveId
                        self.slaveAddr = self.slaveOfSlaveAddr
                        '''
                        With PUB this is a server
                        listCommunication.close()
                        listCommunication = self.initConnection()
                        '''
                        self.logger.debug('I\'m Writer ' + self.threadId + ' and i have a new slave : ' + self.slaveId + '. Now wait for sync')
                        listCommunication.sync()
                        self.logger.debug('I\'m Writer ' + self.threadId + ' and the sync is completed')

                        try:
                            listCommunication.send(item)
                        except ZMQError:
                            self.logger.debug('Error sending the message, is the server still running?')
                    else:
                        listCommunication.send(item)
            else:
                self.logger.debug('No ready items in my list (Writer ' + self.threadId + ')')
                time.sleep(random()*0.5)

        # while True:
        '''
        This is not necessary
        for i in xrange(2):
            time.sleep(self.delay)
            while not self.condition.isSet():
                #print 'sleeping (' + self.threadId + ')...'
                self.logger.debug('sleeping ( Writer ' + self.threadId + ')...')
                self.condition.wait()

            self.condition.clear()
            listCommunication.sendFromFile(FILE_PATH + self.threadId + TXT)
            self.logger.debug('Message sent to another node ( Writer ' + self.threadId + ') to ' + self.slaveId)
            self.logger.debug("My work is done ( Writer " + self.threadId + ") " + " " + threadName + " " + time.ctime(time.time()))
        '''

if __name__ == '__main__':
    # Create new threads
    #thread2 = WritingThread([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    #thread1 = WritingThread([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    #thread2.start()
    #thread1.start()

    print "Exiting Main Thread"