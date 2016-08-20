#! /usr/bin/env python

import threading
import time


class ListThread:
    def __init__(self, threadId, slave, slaveOfSlave, masterMemory, slaveMemory):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.slave = slave
        self.slaveOfSlave = slaveOfSlave
        self.masterM = masterMemory
        self.slaveM = slaveMemory

    def run(self):
        print "Starting " + self.threadId
        self.printInfo(self.threadId, 2)
        print "Exiting " + self.threadId

    def printInfo(threadName, counter):
        time.sleep(counter)
        print "I am : ", threadName, time.ctime(time.time())

if __name__ == '__main__':
    # Create new threads
    thread1 = ListThread(1, 2, -1, [0, 127], [0, 127])
    thread2 = ListThread(2, 1, -1, [0, 127], [0, 127])

    # Start new Threads
    thread1.start()
    thread2.start()

    print "Exiting Main Thread"
