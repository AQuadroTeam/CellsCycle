from threading import Thread
import zmq
from Queue import Queue
from binascii import crc32
from CellCycle.MemoryModule import MemoryManagement

def startExtraCycleListeners(settings, logger):
    threadNumber = settings.getServiceThreadNumber()
    port = settings.getClientEntrypointPort()

    # prepare socket urls
    url_Frontend = "tcp://*:" + str(port)

    # Prepare our context and sockets
    context = zmq.Context.instance()

    socket = context.socket(zmq.STREAM)
    socket.bind(url_Frontend)

    queue = Queue()

    for i in range(threadNumber):
        th = Thread(name='ServiceEntrypointThread',target=_serviceThread, args=(settings, logger, url_Frontend, socket, queue))
        th.start()

    Thread(name='ServiceEntrypointRouterThread',target=_receiverThread, args=(logger, socket, queue)).start()


def _receiverThread(logger, socket, queue):
    while True:
        client, command = socket.recv_multipart()
        queue.put([client, command])


def _serviceThread(settings, logger, url_Backend,socket,queue):
    logger.debug("Listening for clients on " + url_Backend)
    while True:
        client, message = queue.get()
        if(message != ""):

            logger.debug( "received service command: " + str(message))
            command = message.split()
            try:
                _manageRequest(settings, socket, command, client)
            except Exception as e:
                logger.warning("Error for client: "+ str(client) +", error:"+ str(e))


def _manageRequest(settings, socket, command, client):
    GET = "GET"
    SET = "SET"
    QUIT = "QUIT"
    if(command[0].upper() == GET):
        if(command[1] != ""):
            key = hashOfKey(command[1])
            _getHandler(settings, socket, client, key)
            return;
        else:
            _sendGuide(socket, client)
            return;
    elif(command[0].upper() == SET):
        if(len(command) < 5):
            _sendGuide(socket, client)
            return;
        else:
            key = hashOfKey(command[1])
            flag = command[2]
            exp = command[3]
            byte = command[4]

            try:
                value = " ".join(command[5:])
            except Exception as e:
                _sendGuide(socket, client)
                return

            try:
                _setHandler(settings, socket,client, key, flag, exp, byte, value)
            except Exception as e:
                print "qui errore"+ str(e)
                _sendError(socket, client)

            return
    elif(command[0].upper() == QUIT):
        _quitHandler(settings, socket, client)
        return
    else:
        _sendGuide(socket, client)
        return



def _send(socket, client, data):
    socket.send_multipart([client,data])

def _sendGuide(socket, client):
    guide = "ERROR\r\nSUPPORTED OPERATIONS:\n-SET (SET <key> <flag> <exp> <byte> <data>)\n-GET (SET <key> <data>)\n\nBYE\n"
    _send(socket, client, guide)

def _sendError(socket, client):
    error = "ERROR\r\n"
    _send(socket, client, error)

def _setHandler(settings, socket,client, key, flag, exp, byte, value):
    #add flag to stored data
    value = '{:010d}'.format(int(flag)) + value;
    #get host address
    returnValue = MemoryManagement.standardMasterSetRequest(settings, key, value)
    returnString = "STORED\n"
    _send(socket, client, returnString)

def _getHandler(settings, socket, client, key):
    returnValue = MemoryManagement.standardMasterGetRequest(settings, key)
    returnValue = returnValue if returnValue!=None else ""
    if(len(returnValue)>=10):
        flag = int(returnValue[:10])
        data = returnValue[10:]

        returnString = "VALUE " + str(key) +" "+ str(flag) +" "+ str(len(data)) +"  \n"+ data + "\r\nEND\n"
    else:
        returnString = "NOT_FOUND\n"
    _send(socket, client, returnString)

def _quitHandler(settings, socket, client):
    _send(socket, client, b'')

def hashOfKey(key):
    return crc32(key) % (1<<32)
