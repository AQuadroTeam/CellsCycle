#! /usr/bin/env python

from ListThread import ListThread
import time
from CellCycle.Settings import SettingsManager
from ListCommunication import ListCommunication

FILE_PATH = "./my_list.txt"
DEAD = 'DEAD'


class ReadingThread(ListThread):
    def __init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory):
        ListThread.__init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory)
        self.settingsManager = SettingsManager.SettingsManager()
        self.settingsObject = None

    def run(self):
        print "Starting " + self.threadId
        self.readList(self.threadId, 2)
        print "Exiting " + self.threadId

    def readList(self, threadName, counter):
        listCommunication = ListCommunication()

        if self.threadId > self.prevId:
            print "I am the first : ", threadName, time.ctime(time.time())
            listCommunication.initClientSocket()
            listCommunication.startClientConnection()
            # not necessary self.settingsManager.readConfigurationFromFile(FILE_PATH)
            # if self.threadId in self.settingsManager.settings.configDict :
            self.settingsManager.settings = SettingsManager.SettingsObject({})
            self.settingsManager.settings.configDict[self.threadId] = [str(time.ctime(time.time()))]

            print "This is the dictionary in this moment :"
            print self.settingsManager.settings.configDict

            self.settingsManager.writeFileFromConfiguration(FILE_PATH)
            listCommunication.sendFromFile(FILE_PATH)
        else:
            print "I am not the first : ", threadName, time.ctime(time.time())
            listCommunication.initServerSocket()

        while True:
            print 'sleeping...'
            time.sleep(counter)
            print 'awake!'
            message = listCommunication.recv()

            if len(message) == 0:
                listCommunication.storeData(self.prevId + ' ' + DEAD, FILE_PATH)
            else:
                listCommunication.storeData(message, FILE_PATH)

            print "I've just received this message"
            print message

            print "I am : ", threadName, time.ctime(time.time())
            self.settingsManager.readConfigurationFromFile(FILE_PATH)
            # if self.threadId in self.settingsManager.settings.configDict :
            self.settingsManager.settings.configDict[self.threadId] = [str(time.ctime(time.time()))]
            print "This is the dictionary in this moment :"
            print self.settingsManager.settings.configDict
            self.settingsManager.writeFileFromConfiguration(FILE_PATH)
            # else :
            #     self.settingsManager.writeFileFromConfiguration(FILE_PATH)
            listCommunication.sendFromFile(FILE_PATH)


if __name__ == '__main__':
    # Create new threads
    thread2 = ReadingThread(1, 2, 2, None, [0, 127], [0, 127])
    thread1 = ReadingThread(2, 1, 1, None, [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"
