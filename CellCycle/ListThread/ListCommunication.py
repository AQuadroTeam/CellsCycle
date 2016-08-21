import socket
import time

BACKLOG = 5

class ListCommunication :

    def __init__(self):
        self.port = 9999
        # get local machine name
        self.host = socket.gethostname()
        # create a socket object
        self.communicationSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def initServerSocket(self):
        # bind to the port
        self.communicationSocket.bind((self.host, self.port))

        # queue up to BACKLOG requests
        self.communicationSocket.listen(BACKLOG)

    def startServerAccept(self):
        while True:
            # establish a connection
            clientSocket,addr = self.communicationSocket.accept()

            print("Got a connection from %s" % str(addr))
            currentTime = time.ctime(time.time()) + "\r\n"
            clientSocket.send(currentTime.encode('ascii'))
            clientSocket.close()

    def startClientConnection(self):
        # connection to hostname on the port.
        self.communicationSocket.connect((self.host, self.port))

    def startClientReceive(self):
        # Receive no more than 1024 bytes
        tm = self.communicationSocket.recv(1024)
        self.communicationSocket.close()

        print("The time got from the server is %s" % tm.decode('ascii'))