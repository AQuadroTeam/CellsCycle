#! /usr/bin/env python

# from ChainModule import ChainModule
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
    def __init__(self, threadId, prevId, slave, slave_of_slave, masterMemory, slaveMemory, logger, condition, delay):
        ProducerThread.__init__(self, threadId, prevId, slave, slave_of_slave, masterMemory, slaveMemory, logger, condition, delay)
        self.logger.debug("These are my features (Reader): (" + self.myself + ") Master ID : " + self.masterId + " SlaveID: " + self.slaveId)
        self.settingsManager = SettingsManager.SettingsManager()
        self.settingsObject = None

    def run(self):
        #time.sleep(int(self.myself))
        print "Starting Reader " + self.myself
        self.readList(self.myself, 2)
        print "Exiting Reader " + self.myself

    # def set_proper_timeout(self, nodes=DEF_NODES, special_lap=False):
    #    if special_lap:
    #        index_timeout = int(self.myself) - 1
    #        change_timeout = index_timeout % nodes
    #        node_timeout = (change_timeout + 1)*nodes
        # else:


    def readList(self, threadName, counter):
        listCommunication = ListCommunication(DEFAULT_ADDR,self.threadAddr)

        '''
        You don't need to check if you are the first
        if self.myself < self.prevId:
            print "I am not the first : ", threadName, time.ctime(time.time())
            listCommunication.initServerSocket()
        '''

        listCommunication.external_channel_publish()

        # just to see if it's a condition problem
        # time.sleep(0.1)

        while True:
        # for i in xrange(2):
            '''
            You don't need to sleep
            print 'sleeping...'
            time.sleep(counter)
            print 'awake!'
            '''
            try:
                # timeStart = time.time()
                message = listCommunication.wait_ext_message()
                # timeEnd = time.time()

                # Will will not use files anymore
                # listCommunication.storeData(message, FILE_PATH + self.myself + TXT)

                self.produce(message)

                #self.logger.debug("I'm a READER , it's passed " + str((timeEnd - timeStart)) + " , i've just received this message (" + self.myself + ") from myself " + self.masterId + ", " + self.masterAddr + " : " + message)
                self.logger.debug("I'm a READER , i've just received this message (" + self.myself + ") from myself " + self.masterId + ", " + self.masterAddr + " : " + message)
                # print "I've just received this message (" + self.myself + ") from myself " + self.masterId
                # print message

                '''
                You don't need to send something
                print "I am : ", threadName, time.ctime(time.time())
                self.settingsManager.readConfigurationFromFile(FILE_PATH)
                # if self.myself in self.settingsManager.settings.configDict :
                self.settingsManager.settings.configDict[self.myself] = [str(time.ctime(time.time()))]
                print "This is the dictionary at this moment :"
                print self.settingsManager.settings.configDict
                self.settingsManager.writeFileFromConfiguration(FILE_PATH)
                # else :
                #     self.settingsManager.writeFileFromConfiguration(FILE_PATH)
                listCommunication.sendFromFile(FILE_PATH)

                # hard-coded check if is still alive
                #if self.myself == '1':
                #    counter = 10
                '''
            except Again:
                '''
                Not necessary because we wait forever
                #print "Message not ready"
                self.logger.debug("Message not ready from (Reader " + self.myself + ") : " + self.masterId)
                if not hasattr(self.settingsManager.settings,'configDict') :
                    self.settingsManager.settings = SettingsManager.SettingsObject({})
                self.settingsManager.settings.configDict[self.masterId] = [DEAD]
                self.settingsManager.settings.configDict[self.myself] = [str(time.ctime(time.time()))]

                #print "This is the dictionary at this moment (" + self.myself + ") :"
                self.logger.debug("This is the dictionary at this moment (" + self.myself + ") :")
                #print self.settingsManager.settings.configDict
                self.logger.debug(self.settingsManager.settings.configDict)
                self.settingsManager.writeFileFromConfiguration(FILE_PATH + self.myself + TXT)
                # else :
                #     self.settingsManager.writeFileFromConfiguration(FILE_PATH)
                '''
                '''
                You don't need to send something
                listCommunication.sendFromFile(FILE_PATH)
                '''
            #finally:
            # We will not use conditions anymore
            # self.condition.set()
            # self.logger.debug('Event notified by ' + self.myself + ' , so the writer must sleep for ' + str(self.delay))


if __name__ == '__main__':
    # Create new threads
    thread2 = ReadingThread([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = ReadingThread([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"
