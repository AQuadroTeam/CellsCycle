#! /usr/bin/env python

from ListThread import ListThread
import time


class ReadingThread (ListThread):

    def __init__(self, threadId, slave, slaveOfSlave, masterMemory, slaveMemory):
        ListThread.__init__(self, threadId, slave, slaveOfSlave, masterMemory, slaveMemory)
        self.list = None

    def run(self):
        print "Starting " + self.threadId
        self.readList(self.threadId, 2)
        print "Exiting " + self.threadId


    def readList(threadName, counter):
        time.sleep(counter)
        print "I am : ", threadName, time.ctime(time.time())


# Create new threads
thread1 = ListThread(1, 2, -1, [0,127],[0,127])
thread2 = ListThread(2, 1, -1, [0,127],[0,127])

# Start new Threads
thread1.start()
thread2.start()

print "Exiting Main Thread"