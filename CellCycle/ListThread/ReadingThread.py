#! /usr/bin/env python

from ListThread import ListThread
import time
from ..Settings.SettingsManager import SettingsManager

FILE_PATH = "./my_list.txt"


class ReadingThread (ListThread):

    def __init__(self, threadId, slave, slaveOfSlave, masterMemory, slaveMemory):
        ListThread.__init__(self, threadId, slave, slaveOfSlave, masterMemory, slaveMemory)
        self.settingsManager = SettingsManager()
        self.settingsObject = None

    def run(self):
        print "Starting " + self.threadId
        self.readList(self.threadId, 2)
        print "Exiting " + self.threadId

    def readList(self, threadName, counter):

        while True:
            time.sleep(counter)
            print "I am : ", threadName, time.ctime(time.time())
            self.settingsManager.readConfigurationFromFile(FILE_PATH)
            # if self.threadId in self.settingsManager.settings.configDict :
            self.settingsManager.settings.configDict[self.threadId] = [str(time.ctime(time.time()))]
            self.settingsManager.writeFileFromConfiguration(FILE_PATH)
            # else :
            #     self.settingsManager.writeFileFromConfiguration(FILE_PATH)


if __name__ == '__main__':
    # Create new threads
    thread1 = ListThread(1, 2, -1, [0,127],[0,127])
    thread2 = ListThread(2, 1, -1, [0,127],[0,127])

    # Start new Threads
    thread1.start()
    thread2.start()

    print "Exiting Main Thread"