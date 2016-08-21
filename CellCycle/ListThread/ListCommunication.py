import time
import zmq

BACKLOG = 5
MAX_BUFF = 1024
FILE_PATH = "./my_list.txt"


class ListCommunication:

    def __init__(self):
        # create a socket object
        context = zmq.Context()
        self.communicationSocket = context.socket(zmq.REP)

    def initServerSocket(self):
        # bind to the port
        self.communicationSocket.bind("tcp://*:5555")

    def recv(self):
        #  Wait for next request
        message = self.communicationSocket.recv()
        print("Received request")
        return message

    def startClientConnection(self):
        # connection to hostname on the port.
        self.communicationSocket.connect("tcp://localhost:5555")

    def send(self,data):
        #  Send something to another node
        self.communicationSocket.send(data)
        print 'Message sent to another node'

'''
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send(b"World")
'''