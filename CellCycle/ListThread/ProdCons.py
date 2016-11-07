#! /usr/bin/env python

import threading
import time
import logging
import random
import Queue
from Queue import Empty
from ListThread import ListThread

#logging.basicConfig(level=logging.DEBUG,
#                    format='(%(threadName)-9s) %(message)s',)

BUF_SIZE = 10
q = Queue.Queue(BUF_SIZE)


class ProducerThread(ListThread):
    def __init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay):
        ListThread.__init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay)

    def run(self):
        while True:
            '''
            if not q.full():
                item = random.randint(1,10)
                q.put(item)
                logging.debug('Putting ' + str(item)
                              + ' : ' + str(q.qsize()) + ' items in queue')
                time.sleep(random.random())
            '''
            if self.produce(random.randint(1,10)):
                time.sleep(random.random())

        return

    def produce(self,item):
        if not q.full():
            q.put_nowait(item)
            return True
        else:
            return False

class ConsumerThread(ListThread):
    def __init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay):
        ListThread.__init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay)

    def run(self):
        while True:
            '''
            if not q.empty():
                item = q.get()
                logging.debug('Getting ' + str(item)
                              + ' : ' + str(q.qsize()) + ' items in queue')
                time.sleep(random.random())
            '''
            item = self.consume()
            if item is not None:
                time.sleep(random.random())
        return

    def consume(self):
        try:
            return q.get_nowait()
        except Empty:
            return None

        # return q.get() if not q.empty() else None

if __name__ == '__main__':

    p = ProducerThread(name='producer')
    c = ConsumerThread(name='consumer')

    p.start()
    time.sleep(2)
    c.start()
    time.sleep(2)
