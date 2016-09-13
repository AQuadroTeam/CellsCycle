#! /usr/bin/env python

from ListThread import ListThread
import time
from ListCommunication import ListCommunication
from CellCycle.Settings import SettingsManager
from zmq import Again
from random import randint


FILE_PATH = './my_list'
DEAD = 'DEAD'
DEFAULT_ADDR = 'localhost'
TXT = '.txt'
COUNTER = 1


class WritingThread (ListThread):

    def __init__(self, threadId, master, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay):
        ListThread.__init__(self, threadId, master, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay)
        self.logger.debug("These are my features (Writer): (" + self.threadId + ") Master ID : " + self.masterId + " SlaveID: " + self.slaveId)
        self.settingsManager = SettingsManager.SettingsManager()
        self.settingsObject = None

    def run(self):
        #sleep_index = int(self.threadId) % 3 + 1
        #time.sleep(sleep_index)
        print "Starting Writer " + self.threadId
        self.writeList(self.threadId, COUNTER)
        print "Exiting Writer " + self.threadId

    def writeList(self, threadName, counter):

        listCommunication = ListCommunication(DEFAULT_ADDR,self.slaveAddr)
        listCommunication.initClientSocket()
        listCommunication.startClientConnection()

        if self.threadId < self.masterId:
            #print "I am the first (" + self.threadId + "): ", threadName, time.ctime(time.time())
            self.logger.debug("I am the first to write (" + self.threadId + ", my master is " + self.masterId + "): " + " " + threadName + " " + time.ctime(time.time()))

            '''
            You don't need to check if you are the first
            listCommunication.initClientSocket()
            listCommunication.startClientConnection()
            '''
            # not necessary self.settingsManager.readConfigurationFromFile(FILE_PATH)
            # if self.threadId in self.settingsManager.settings.configDict :
            self.settingsManager.settings = SettingsManager.SettingsObject({})
            self.settingsManager.settings.configDict[self.threadId] = [str(time.ctime(time.time()))]

            #print "This is the dictionary at this moment (" + self.threadId + "):"
            self.logger.debug("This is the dictionary at this moment ( Writer " + self.threadId + "):")
            #print self.settingsManager.settings.configDict
            self.logger.debug(self.settingsManager.settings.configDict)

            self.settingsManager.writeFileFromConfiguration(FILE_PATH + self.threadId +TXT)
            listCommunication.sendFromFile(FILE_PATH + self.threadId + TXT)
            self.logger.debug('Message sent to another node ( Writer ' + self.threadId + ') to ' + self.slaveId)

        # just a check for dead nodes
        if self.threadId == '1':
            time.sleep(100000000000000000)

        #while True:
        for i in xrange(2):
            time.sleep(self.delay)
            while not self.condition.isSet():
                #print 'sleeping (' + self.threadId + ')...'
                self.logger.debug('sleeping ( Writer ' + self.threadId + ')...')
                self.condition.wait()

            self.condition.clear()
            #print 'awake (' + self.threadId + ') !'
            self.logger.debug('awake ( Writer ' + self.threadId + ') !')
            #print "I am : ", threadName, time.ctime(time.time())
            self.logger.debug("I am a writer : " + threadName + " " + time.ctime(time.time()))

            self.settingsManager.readConfigurationFromFile(FILE_PATH + self.threadId + TXT)
            # if self.threadId in self.settingsManager.settings.configDict :
            # This is an old version to write a file self.settingsManager.settings.configDict[self.threadId] = [str(time.ctime(time.time()))]
            # self.settingsManager.settings.configDict[self.threadId] = []
            self.settingsManager.settings.configDict[self.threadId] = [str(time.ctime(time.time()))]
            #print "This is the dictionary at this moment (" + self.threadId + "):"
            self.logger.debug("This is the dictionary at this moment ( Writer " + self.threadId + "):")
            #print self.settingsManager.settings.configDict
            self.logger.debug(self.settingsManager.settings.configDict)
            self.settingsManager.writeFileFromConfiguration(FILE_PATH + self.threadId + TXT)
            # else :
            #     self.settingsManager.writeFileFromConfiguration(FILE_PATH)
            listCommunication.sendFromFile(FILE_PATH + self.threadId + TXT)
            self.logger.debug('Message sent to another node ( Writer ' + self.threadId + ') to ' + self.slaveId)
            #print "My work is done (" + self.threadId + ") ", threadName, time.ctime(time.time())
            self.logger.debug("My work is done ( Writer " + self.threadId + ") " + " " + threadName + " " + time.ctime(time.time()))
            # hard-coded check if is still alive
            #if self.threadId == '1':
            #    time.sleep(100000000000000000)
            #counter = 100000000


if __name__ == '__main__':
    # Create new threads
    thread2 = WritingThread([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = WritingThread([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"