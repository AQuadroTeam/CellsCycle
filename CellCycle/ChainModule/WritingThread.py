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
PRIORITY_ALIVE = '0'


class WritingThread (ListThread):

    def __init__(self, threadId, master, slave, slave_of_slave, masterMemory, slaveMemory, logger, condition, delay):
        ListThread.__init__(self, threadId, master, slave, slave_of_slave, masterMemory, slaveMemory, logger, condition, delay)
        self.logger.debug("These are my features (Writer): (" + self.myself + ") Master ID : " + self.masterId + " SlaveID: " + self.slaveId)
        self.settingsManager = SettingsManager.SettingsManager()
        self.settingsObject = None

    def run(self):
        # sleep_index = int(self.myself) % 3 + 1
        # time.sleep(sleep_index)
        print "Starting Writer " + self.myself
        self.writeList(self.myself, COUNTER)
        print "Exiting Writer " + self.myself

    def writeList(self, threadName, counter):

        listCommunication = ListCommunication(DEFAULT_ADDR,self.slaveAddr)
        listCommunication.external_channel_subscribe()
        listCommunication.start_client_connection()

        # just a check for dead nodes
        if self.myself == '1':
            time.sleep(100000000000000000)

        # for i in xrange(2):
        while True:
            time.sleep(0.5)
            self.logger.debug('Send that i\'m ALIVE (' + self.myself + ') to ' + self.slaveId)
            listCommunication.forward(self.myself + ' ' + PRIORITY_ALIVE)
            # send(self.myself + 'ALIVE')

        '''
        This thread only sends an advisory to the next one
        if self.myself < self.masterId:
            #print "I am the first (" + self.myself + "): ", threadName, time.ctime(time.time())
            self.logger.debug("I am the first to write (" + self.myself + ", my master is " + self.masterId + "): " + " " + threadName + " " + time.ctime(time.time()))
        '''
        '''
        You don't need to check if you are the first
        listCommunication.initClientSocket()
        listCommunication.startClientConnection()
        '''
        '''
        This thread only sends an advisory to the next one
            # not necessary self.settingsManager.readConfigurationFromFile(FILE_PATH)
            # if self.myself in self.settingsManager.settings.configDict :
            self.settingsManager.settings = SettingsManager.SettingsObject({})
            self.settingsManager.settings.configDict[self.myself] = [str(time.ctime(time.time()))]

            #print "This is the dictionary at this moment (" + self.myself + "):"
            self.logger.debug("This is the dictionary at this moment ( Writer " + self.myself + "):")
            #print self.settingsManager.settings.configDict
            self.logger.debug(self.settingsManager.settings.configDict)

            self.settingsManager.writeFileFromConfiguration(FILE_PATH + self.myself +TXT)
            listCommunication.sendFromFile(FILE_PATH + self.myself + TXT)
            self.logger.debug('Message sent to another node ( Writer ' + self.myself + ') to ' + self.slaveId)

        # just a check for dead nodes
        if self.myself == '1':
            time.sleep(100000000000000000)

        #while True:
        for i in xrange(2):
            time.sleep(self.delay)
            while not self.condition.isSet():
                #print 'sleeping (' + self.myself + ')...'
                self.logger.debug('sleeping ( Writer ' + self.myself + ')...')
                self.condition.wait()

            self.condition.clear()
            #print 'awake (' + self.myself + ') !'
            self.logger.debug('awake ( Writer ' + self.myself + ') !')
            #print "I am : ", threadName, time.ctime(time.time())
            self.logger.debug("I am a writer : " + threadName + " " + time.ctime(time.time()))

            self.settingsManager.readConfigurationFromFile(FILE_PATH + self.myself + TXT)
            # if self.myself in self.settingsManager.settings.configDict :
            # This is an old version to write a file self.settingsManager.settings.configDict[self.myself] = [str(time.ctime(time.time()))]
            # self.settingsManager.settings.configDict[self.myself] = []
            self.settingsManager.settings.configDict[self.myself] = [str(time.ctime(time.time()))]
            #print "This is the dictionary at this moment (" + self.myself + "):"
            self.logger.debug("This is the dictionary at this moment ( Writer " + self.myself + "):")
            #print self.settingsManager.settings.configDict
            self.logger.debug(self.settingsManager.settings.configDict)
            self.settingsManager.writeFileFromConfiguration(FILE_PATH + self.myself + TXT)
            # else :
            #     self.settingsManager.writeFileFromConfiguration(FILE_PATH)
            listCommunication.sendFromFile(FILE_PATH + self.myself + TXT)
            self.logger.debug('Message sent to another node ( Writer ' + self.myself + ') to ' + self.slaveId)
            #print "My work is done (" + self.myself + ") ", threadName, time.ctime(time.time())
            self.logger.debug("My work is done ( Writer " + self.myself + ") " + " " + threadName + " " + time.ctime(time.time()))
            # hard-coded check if is still alive
            #if self.myself == '1':
            #    time.sleep(100000000000000000)
            #counter = 100000000
        '''

if __name__ == '__main__':
    # Create new threads
    thread2 = WritingThread([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = WritingThread([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"