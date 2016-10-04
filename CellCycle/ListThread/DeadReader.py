#! /usr/bin/env python

#from ListThread import ListThread
from ProdCons import ProducerThread
from ListCommunication import ListCommunication
from zmq import Again
from random import randint
# from Queue import Queue

FILE_PATH = './my_list'
DEAD = 'DEAD'
PRIORITY_DEAD = '3'
PRIORITY_ALIVE = '0'
PRIORITY_ADD = '2'
DEFAULT_ADDR = '127.0.0.1'
TXT = '.txt'
DEF_NODES = 3
BUF_SIZE = 10
# node_queue = Queue(BUF_SIZE)

class DeadReader(ProducerThread):
    def __init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay):
        ProducerThread.__init__(self, threadId, prevId, slave, slaveOfSlave, masterMemory, slaveMemory, logger, condition, delay)
        self.logger.debug("These are my features (Reader): (" + self.threadId + ") Master ID : " + self.masterId + " SlaveID: " + self.slaveId)
        self.dead_message = ''
        self.last_version = 1

    def run(self):
        # time.sleep(int(self.threadId))
        print "Starting Reader " + self.threadId
        self.waitForADead(self.threadId, 2)
        print "Exiting Reader " + self.threadId

    # def set_proper_timeout(self, nodes=DEF_NODES, special_lap=False):
    #    if special_lap:
    #        index_timeout = int(self.threadId) - 1
    #        change_timeout = index_timeout % nodes
    #        node_timeout = (change_timeout + 1)*nodes
        # else:

    def initConnection(self):
        # We have to subscribe to our master
        listCommunication = ListCommunication(DEFAULT_ADDR,self.masterAddr)
        listCommunication.initClientSocket()
        self.logger.debug('Writer ' + self.threadId + ' waiting for sync with node ' + self.slaveId + ' with address ' + listCommunication.completeAddress)
        listCommunication.startClientConnection()
        self.logger.debug('Sync completed. New client socket (Writer ' + self.threadId + ') to node ' + self.slaveId + ' with address ' + listCommunication.completeAddress)
        return listCommunication

    def renewConnection(self):
        # Troppo hardcoded
        listCommunication = ListCommunication(DEFAULT_ADDR,'5186')
        listCommunication.initClientSocket()
        self.logger.debug('Writer ' + self.threadId + ' waiting for sync with node ' + self.slaveId + ' with address ' + listCommunication.completeAddress)
        listCommunication.startClientConnection()
        self.logger.debug('Sync completed. New client socket (Writer ' + self.threadId + ') to node ' + self.slaveId + ' with address ' + listCommunication.completeAddress)
        return listCommunication

    def waitForADead(self, threadName, counter):

        '''
        With SUB this is a client
        listCommunication = ListCommunication(DEFAULT_ADDR,self.threadAddr)
        listCommunication.initServerSocket()
        '''
        listCommunication = self.initConnection()

        while True:
        # for i in xrange(2):

            try:
                # timeStart = time.time()
                message = listCommunication.recv()
                # timeEnd = time.time()

                if message[2] != PRIORITY_ALIVE:

                    if message[2] == PRIORITY_DEAD and message[9] == self.threadId:
                        self.logger.debug('Ok i\'m DEAD.. ' + self.threadId + ' Goodbye everyone!')
                        listCommunication.close()
                        return

                    if message[2] == PRIORITY_ADD and message[9] < self.slaveId:
                        self.logger.debug('New node added, i\'m reader ' + self.threadId)
                        # This is the part when i connect to another publisher
                        listCommunication.close()
                        listCommunication = self.initConnection()
                        # this could be risky
                        self.dead_message = ''
                        message = self.dead_message

                    if not (message[11] in self.node_list):
                        if message[2] == PRIORITY_DEAD:
                            self.logger.debug('Hey you are not in the list!')
                        else:
                            self.logger.debug('Hey ' + message[11] + 'you are not in the list! You are supposed to be dead!')

                    if message != self.dead_message:
                        if self.dead_message != '':
                            sent_version = self.dead_message[0]
                            received_version = message[0]
                            sent_priority = self.dead_message[2]
                            received_priority = message[2]
                            sent_random = self.dead_message[4:8]
                            received_random = message[4:8]
                            if received_version == sent_version and (sent_priority > received_priority or sent_random > received_random):
                                self.produce(message)
                            elif received_version > sent_version:
                                self.produce(message)
                        else:
                            self.logger.debug('I\'ve never generated a message (' + self.threadId + ') infact my dead_message\'s length is ' + str(len(self.dead_message)) )
                            self.produce(message)
                    else:
                        self.logger.debug("I'm a READER FOR A DEAD , (" + self.threadId + ") and THE CYCLE IS OVER!")

                # Not necessary
                # if not node_queue.full():
                #    node_queue.put_nowait(message)

                # Well done
                self.logger.debug("I'm a READER FOR A DEAD , i've just received this message (" + self.threadId + ") from threadId " + self.masterId + ", " + self.masterAddr + " : " + message)

            except Again:
                # Not necessary
                # if not node_queue.full():
                #     node_queue.put_nowait(DEAD)
                self.dead_message = str(self.last_version) + ' ' + PRIORITY_DEAD + ' ' + str(randint(1000,9999)) + ' ' + self.masterId + ' ' + self.threadId
                if not (self.masterId in self.node_list):
                    self.logger.debug('Probably i missed something')
                    exit(1)
                else:
                    self.logger.debug('I\'m ' + self.threadId + ' and you\'re dead dear ' + self.masterId + ', just remove you from the list and reset the socket')
                    del self.node_list[self.masterId]
                    '''
                    With SUB this is a client
                    # try without reset
                    # listCommunication.reset()
                    '''

                self.produce(self.dead_message)
                self.logger.debug("This is my dead_message (" + self.threadId + ") : " + self.dead_message)
                self.last_version += 1
                self.logger.debug("Message not ready from (Reader " + self.threadId + ") : " + self.masterId)
                # TODO add masterOfMaster
                self.masterId = self.slaveId
                self.masterAddr = self.slaveAddr

                # This is the part when i connect to another publisher
                listCommunication.close()
                listCommunication = self.initConnection()


            #finally:
            # Might be unnecessary
            # self.condition.set()
            #self.logger.debug('Event notified by ' + self.threadId + ' , so the writer must sleep for ' + str(self.delay))


if __name__ == '__main__':
    # Create new threads
    thread2 = DeadReader([1,5555], [2,5556], [2,5556], [], [0, 127], [0, 127])
    thread1 = DeadReader([2,5556], [1,5555], [1,5555], [], [0, 127], [0, 127])

    # Start new Threads
    thread2.start()
    thread1.start()

    print "Exiting Main Thread"
