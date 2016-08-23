#! /usr/bin/env python

from ListThread import ListThread
import time
from ListCommunication import ListCommunication
from CellCycle.Settings import SettingsManager
from zmq import Again

FILE_PATH = './my_list.txt'
DEAD = 'DEAD'
DEFAULT_ADDR = '*'


class WritingThread (ListThread):

    def __init__(self, threadId, master,slave, slaveOfSlave, masterMemory, slaveMemory):
        ListThread.__init__(self, master, threadId, slave, slaveOfSlave, masterMemory, slaveMemory)
        self.settingsManager = SettingsManager.SettingsManager()
        self.settingsObject = None


    def run(self):
        print "Starting " + self.threadId
        self.writeList(self.threadId, 2)
        print "Exiting " + self.threadId


    def writeList(self, threadName, counter):

        listCommunication = ListCommunication(DEFAULT_ADDR,self.slaveAddr)
        listCommunication.initClientSocket()
        listCommunication.startClientConnection()

        if self.threadId > self.masterId:
            print "I am the first : ", threadName, time.ctime(time.time())

            '''
            You don't need to check if you are the first
            listCommunication.initClientSocket()
            listCommunication.startClientConnection()
            '''
            # not necessary self.settingsManager.readConfigurationFromFile(FILE_PATH)
            # if self.threadId in self.settingsManager.settings.configDict :
            self.settingsManager.settings = SettingsManager.SettingsObject({})
            self.settingsManager.settings.configDict[self.threadId] = [str(time.ctime(time.time()))]

            print "This is the dictionary at this moment :"
            print self.settingsManager.settings.configDict

            self.settingsManager.writeFileFromConfiguration(FILE_PATH)
            listCommunication.sendFromFile(FILE_PATH)

        while True:
            print 'sleeping...'
            time.sleep(counter)
            print 'awake!'

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


if __name__ == '__main__':
    # Create new threads
    thread2 = WritingThread([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = WritingThread([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"