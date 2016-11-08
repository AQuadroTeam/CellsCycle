#! /usr/bin/env python

import Queue
from Queue import Empty
from ListThread import ListThread

BUF_SIZE = 10
q = Queue.Queue(BUF_SIZE)


class ProducerThread(ListThread):
    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name):
        ListThread.__init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name)

    def run(self):
        print_string = "I\'m {} and i\'m running".format(self.myself.id)
        self.logger.debug(print_string)

    @staticmethod
    def produce(item):
        if not q.full():
            q.put_nowait(item)
            return True
        else:
            return False


class ConsumerThread(ListThread):
    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name):
        ListThread.__init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name)

    def run(self):
        print_string = "I\'m {} and i\'m running".format(self.myself.id)
        self.logger.debug(print_string)

    @staticmethod
    def consume():
        try:
            return q.get_nowait()
        except Empty:
            return None
