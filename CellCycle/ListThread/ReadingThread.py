#! /usr/bin/env python

# from ListThread import ListThread
import time
from CellCycle.Settings import SettingsManager
from ListCommunication import ListCommunication
from zmq import Again
from ProdCons import ProducerThread

FILE_PATH = './my_list'
DEAD = 'DEAD'
DEFAULT_ADDR = '*'
TXT = '.txt'
DEF_NODES = 3


class ReadingThread(ProducerThread):
    def __init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay):
        ProducerThread.__init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay)
        self.logger.debug("These are my features (Reader): (" + self.threadId + ") Master ID : " + self.masterId + " SlaveID: " + self.slaveId)
        self.settingsManager = SettingsManager.SettingsManager()
        self.settingsObject = None

    def run(self):
        #time.sleep(int(self.threadId))
        print "Starting Reader " + self.threadId
        self.readList(self.threadId, 2)
        print "Exiting Reader " + self.threadId

    # def set_proper_timeout(self, nodes=DEF_NODES, special_lap=False):
    #    if special_lap:
    #        index_timeout = int(self.threadId) - 1
    #        change_timeout = index_timeout % nodes
    #        node_timeout = (change_timeout + 1)*nodes
        # else:


    def readList(self, threadName, counter):
        listCommunication = ListCommunication(DEFAULT_ADDR,self.threadAddr)

        '''
        You don't need to check if you are the first
        if self.threadId < self.prevId:
            print "I am not the first : ", threadName, time.ctime(time.time())
            listCommunication.initServerSocket()
        '''

        listCommunication.initServerSocket()

        # just to see if it's a condition problem
        # time.sleep(0.1)

        # while True:
        for i in xrange(2):
            '''
            You don't need to sleep
            print 'sleeping...'
            time.sleep(counter)
            print 'awake!'
            '''
            try:
                #timeStart = time.time()
                message = listCommunication.recv()
                #timeEnd = time.time()

                # Will will not use files anymore
                # listCommunication.storeData(message, FILE_PATH + self.threadId + TXT)

                self.produce(message)

                #self.logger.debug("I'm a READER , it's passed " + str((timeEnd - timeStart)) + " , i've just received this message (" + self.threadId + ") from threadId " + self.masterId + ", " + self.masterAddr + " : " + message)
                self.logger.debug("I'm a READER , i've just received this message (" + self.threadId + ") from threadId " + self.masterId + ", " + self.masterAddr + " : " + message)
                # print "I've just received this message (" + self.threadId + ") from threadId " + self.masterId
                # print message

                '''
                You don't need to send something
                print "I am : ", threadName, time.ctime(time.time())
                self.settingsManager.readConfigurationFromFile(FILE_PATH)
                # if self.threadId in self.settingsManager.settings.configDict :
                self.settingsManager.settings.configDict[self.threadId] = [str(time.ctime(time.time()))]
                print "This is the dictionary at this moment :"
                print self.settingsManager.settings.configDict
                self.settingsManager.writeFileFromConfiguration(FILE_PATH)
                # else :
                #     self.settingsManager.writeFileFromConfiguration(FILE_PATH)
                listCommunication.sendFromFile(FILE_PATH)

                # hard-coded check if is still alive
                #if self.threadId == '1':
                #    counter = 10
                '''
            except Again:
                '''
                Not necessary because we wait forever
                #print "Message not ready"
                self.logger.debug("Message not ready from (Reader " + self.threadId + ") : " + self.masterId)
                if not hasattr(self.settingsManager.settings,'configDict') :
                    self.settingsManager.settings = SettingsManager.SettingsObject({})
                self.settingsManager.settings.configDict[self.masterId] = [DEAD]
                self.settingsManager.settings.configDict[self.threadId] = [str(time.ctime(time.time()))]

                #print "This is the dictionary at this moment (" + self.threadId + ") :"
                self.logger.debug("This is the dictionary at this moment (" + self.threadId + ") :")
                #print self.settingsManager.settings.configDict
                self.logger.debug(self.settingsManager.settings.configDict)
                self.settingsManager.writeFileFromConfiguration(FILE_PATH + self.threadId + TXT)
                # else :
                #     self.settingsManager.writeFileFromConfiguration(FILE_PATH)
                '''
                '''
                You don't need to send something
                listCommunication.sendFromFile(FILE_PATH)
                '''
            finally:
                # We will not use conditions anymore
                # self.condition.set()
                self.logger.debug('Event notified by ' + self.threadId + ' , so the writer must sleep for ' + str(self.delay))


if __name__ == '__main__':
    # Create new threads
    thread2 = ReadingThread([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = ReadingThread([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"
