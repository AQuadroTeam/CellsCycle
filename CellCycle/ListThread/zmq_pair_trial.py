#! /usr/bin/env python

import zmq
import time
from threading import Thread


class ServerZMQ(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.port = "5556"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.bind("tcp://*:%s" % self.port)

    def server_behaviour(self):
        while True:
            self.socket.send("Server message to client3")
            msg = self.socket.recv()
            print msg
            time.sleep(1)


class ClientZMQ(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.port = "5556"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect("tcp://localhost:%s" % self.port)

    def client_behaviour(self):
        while True:
            msg = self.socket.recv()
            print msg
            self.socket.send("client message to server1")
            self.socket.send("client message to server2")
            time.sleep(1)

if __name__ == '__main__':
    server = ServerZMQ()
    time.sleep(1)
    client = ClientZMQ()

    client.client_behaviour()
    server.server_behaviour()



