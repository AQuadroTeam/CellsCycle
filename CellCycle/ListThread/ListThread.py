#! /usr/bin/env python

import threading
import time


class ListThread (threading.Thread):
    def __init__(self, threadId, master, slave, slaveOfSlave, masterMemory, slaveMemory, logger):
        threading.Thread.__init__(self)
        self.logger = logger
        self.threadId = str(threadId[0])
        self.threadAddr = str(threadId[1])
        self.masterId = str(master[0])
        self.masterAddr = str(master[1])
        self.slaveId = str(slave[0])
        self.slaveAddr = str(slave[1])
        if len(slaveOfSlave) == 0:
            self.slaveOfSlaveId = ''
            self.slaveOfSlaveAddr = ''
        else:
            self.slaveOfSlaveId = str(slaveOfSlave[0])
            self.slaveOfSlaveAddr = str(slaveOfSlave[1])
        self.masterM = masterMemory
        self.slaveM = slaveMemory

    def run(self):
        print "Starting " + self.threadId
        self.printInfo(self.threadId, 2)
        print "Exiting " + self.threadId

    def printInfo(self, threadName, counter):
        time.sleep(counter)
        print "I am : ", threadName, time.ctime(time.time())

if __name__ == '__main__':
    # Create new threads
    thread2 = ListThread([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = ListThread([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"
