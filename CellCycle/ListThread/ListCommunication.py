import time
import zmq

BACKLOG = 5
MAX_BUFF = 1024
MAX_RCVTIMEO = 2000

class ListCommunication:

    def __init__(self, addr="*", port="8080"):
        # create a socket object
        self.context = zmq.Context()
        self.completeAddress = 'tcp://' + addr + ":" + port
        print self.completeAddress

    def initServerSocket(self):
        self.communicationSocket = self.context.socket(zmq.PAIR)
        self.setRcvTimeo()
        #self.communicationSocket.RCVTIMEO = MAX_RCVTIMEO
        # bind to the port
        self.communicationSocket.bind(self.completeAddress)

    def setRcvTimeo(self, timeout=MAX_RCVTIMEO):
        self.communicationSocket.RCVTIMEO = timeout

    def initClientSocket(self):
        self.communicationSocket = self.context.socket(zmq.PAIR)
        # self.communicationSocket.RCVTIMEO = MAX_RCVTIMEO

    def recv(self):
        #  Wait for next request
        message = self.communicationSocket.recv()
        return message

    def startClientConnection(self):
        # connection to hostname on the port.
        # self.communicationSocket.connect("tcp://localhost:5555")
        self.communicationSocket.connect(self.completeAddress)

    def send(self,data):
        #  Send something to another node
        self.communicationSocket.send(data)

    def storeData(self, data, filePath):
        with open(filePath,'w+') as f:
             f.write(data)
             f.close()

    def sendFromFile(self, filePath):
        with open(filePath,'r') as f:
            data= f.read()
            self.send(data)
            f.close()

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