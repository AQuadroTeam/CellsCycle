from threading import Thread
import zmq
from Queue import Queue
from binascii import crc32
from CellCycle.MemoryModule.MemoryManagement import standardKillRequest, standardSlaveSetRequest, standardSlaveGetRequest, standardTransferRequest, standardMasterSetRequest, standardMasterGetRequest


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
            command = message.split()
            try:
                _manageRequest(logger, settings, socket, command, client)
            except Exception as e:
                logger.warning("Error for client: "+ str(client) +", error:"+ str(e) + ". command: " + message)


def _manageRequest(logger, settings, socket, command, client):
    GET = "GET"
    ADD = "ADD"
    DELETE = "DELETE"
    SET = "SET"
    setList = [ADD , SET]
    QUIT = "QUIT"

    if(command[0].upper() == GET):
        if(command[1] != ""):
            key = hashOfKey(command[1])
            _getHandler(settings, socket, client, key)
            return;
        else:
            _sendGuide(socket, client)
            return;
    if(command[0].upper() == DELETE):
        if(command[1] != ""):
            key = hashOfKey(command[1])
            _deleteHandler(settings, socket, client, key)
            return;
        else:
            _sendGuide(socket, client)
            return;
    elif(command[0].upper() in setList):
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
                logger.warning(str(e) + " for command: " + " ".join(command))
                _sendGuide(socket, client)
                return

            try:
                _setHandler(settings, socket,client, key, flag, exp, byte, value)
            except Exception as e:
                logger.warning(str(e) + " for command: " + " ".join(command))
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
    guide = "ERROR\r\nSUPPORTED OPERATIONS:\n"\
        "-SET (SET <key> <flag> <exp> <byte> <data>)\n"\
        "-ADD (ADD <key> <flag> <exp> <byte> <data>)\n"\
        "-GET (SET <key> <data>)\n"\
        "-DELETE (DELETE <key> <data>)\n"\
        "\nBYE\r\n"
    _send(socket, client, guide)

def _sendError(socket, client):
    error = "ERROR\r\n"
    _send(socket, client, error)

def _setHandler(settings, socket,client, key, flag, exp, byte, value):
    #add flag to stored data
    value = '{:010d}'.format(int(flag)) + value;
    #get server node
    #hosts = getNodesForKey(key)
    #standardMasterGetRequest(settings, key, hosts[0].ip)
    returnValue = standardMasterSetRequest(settings, key, value)
    returnString = "STORED\r\n"
    _send(socket, client, returnString)

def _deleteHandler(settings, socket,client, key):
    #get server node
    #hosts = getNodesForKey(key)
    #standardMasterGetRequest(settings, key, hosts[0].ip)
    returnValue = standardMasterSetRequest(settings, key, None)
    returnString = "DELETED\r\n"
    _send(socket, client, returnString)


def _getHandler(settings, socket, client, key):
    #get server nodes and choose
    #hosts = getNodesForKey(key)
    #if(random()>0.5):
    #   standardMasterGetRequest(settings, key, hosts[0].ip)
    #else:
    #   standardSlaveGetRequest(settings, key, hosts[1].ip)
    returnValue = standardMasterGetRequest(settings, key)
    returnValue = returnValue if returnValue!=None else ""

    if(len(returnValue)>=10):
        flag = int(returnValue[:10])
        data = returnValue[10:]

        returnString = "VALUE " + str(key) +" "+ str(flag) +" "+ str(len(data)) +"  \r\n"+ data + "\r\nEND\r\n"
    else:
        returnString = "NOT_FOUND\r\n"
    _send(socket, client, returnString)

def _quitHandler(settings, socket, client):
    _send(socket, client, b'')


def hashOfKey(key):
    return crc32(key) % (1<<32)
