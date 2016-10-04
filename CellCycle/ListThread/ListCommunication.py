import zmq
import time

BACKLOG = 5
MAX_BUFF = 1024
MAX_RCVTIMEO = 2000

class ListCommunication:

    def __init__(self, addr="*", port="8080"):
        # create a socket object
        self.context = zmq.Context()
        self.completeAddress = 'tcp://' + addr + ":" + port
        self.syncaddress = 'tcp://' + addr + ":"
        if port == '5555':
            self.syncaddress = self.syncaddress + '5562'
        elif port == '5556':
            self.syncaddress = self.syncaddress + '5563'
        elif port == '5557':
            self.syncaddress = self.syncaddress + '5564'


    def initServerSocket(self):
        print 'Generating server connection point ' + self.completeAddress
        self.communicationSocket = self.context.socket(zmq.PUB)
        # This is no necessary as we are talking about a client
        # try without the sndhwm
        # self.communicationSocket.sndhwm = 1100000
        #self.communicationSocket.RCVTIMEO = MAX_RCVTIMEO
        # bind to the port
        self.communicationSocket.bind(self.completeAddress)
        self.open_rep_socket()
        self.sync()

    def open_rep_socket(self, syncAddr=None):
        # Socket to receive signals
        self.syncservice = self.context.socket(zmq.REP)
        if syncAddr is not None:
            self.syncservice.bind(syncAddr)
        else:
            self.syncservice.bind(self.syncaddress)

    def sync(self):

        # wait for synchronization request
        msg = self.syncservice.recv()

        # send synchronization reply
        self.syncservice.send(b'')


    def setRcvTimeo(self, timeout=MAX_RCVTIMEO):
        self.communicationSocket.RCVTIMEO = timeout

    def initClientSocket(self):
        print 'Generating client connection point ' + self.completeAddress

        self.communicationSocket = self.context.socket(zmq.SUB)
        # This is necessary because a subscriber needs a timeout for updates
        self.setRcvTimeo()

        # self.communicationSocket.RCVTIMEO = MAX_RCVTIMEO

    def recv(self):
        #  Wait for next request
        message = self.communicationSocket.recv()
        return message

    def startClientConnection(self, port=None):
        # connection to hostname on the port.
        # self.communicationSocket.connect("tcp://localhost:5555")
        if port is not None: self.completeAddress = 'tcp://localhost:' + port
        self.communicationSocket.connect(self.completeAddress)
        self.communicationSocket.setsockopt(zmq.SUBSCRIBE, b'')

        time.sleep(0.1)

        self.sync_client()

    def open_req_socket(self, syncAddr=None):

        # Second, synchronize with publisher
        self.syncclient = self.context.socket(zmq.REQ)
        if syncAddr is not None:
            self.syncclient.connect(syncAddr)
        else:
            self.syncclient.connect(self.syncaddress)

    def sync_client(self):
        self.open_req_socket()

        # send a synchronization request
        self.syncclient.send(b'')

        # wait for synchronization reply
        self.syncclient.recv()

        # self.communicationSocket.setsockopt(zmq.SUBSCRIBE, '')

    def send(self,data):
        #  Send so
        # mething to another node
        self.communicationSocket.send(data)

    def close(self):
        self.communicationSocket.close()
        self.context.destroy()
        print 'Closing socket with ' + self.completeAddress
        #self.communicationSocket.disconnect(self.completeAddress)

    def reset(self):
        self.communicationSocket.close()
        self.context.destroy()
        self.context = zmq.Context()
        # try without a restart because we can have an address already in use
        self.initServerSocket()

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