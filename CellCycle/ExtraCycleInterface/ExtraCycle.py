from threading import Thread
import zmq
from Queue import Queue
from binascii import crc32

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
        th = Thread(name='ServiceEntrypointThread',target=_serviceThread, args=(logger, url_Frontend, socket, queue))
        th.start()

    Thread(name='ServiceEntrypointRouterThread',target=_receiverThread, args=(logger, socket, queue)).start()


def _receiverThread(logger, socket, queue):
    while True:
        client, command = socket.recv_multipart()
        queue.put([client, command])


def _serviceThread(logger, url_Backend,socket,queue):
    logger.debug("Listening for clients on " + url_Backend)
    while True:
        client, message = queue.get()
        if(message != ""):

            logger.debug( "received service command: " + str(message))
            command = message.split()
            try:
                _manageRequest(socket, command, client)
            except Exception as e:
                logger.warning("Error for client: "+ str(client) +", error:"+ str(e))


def _manageRequest(socket, command, client):
    GET = "GET"
    SET = "SET"
    if(command[0].upper() == GET):
        if(command[1] != ""):
            key = hashOfKey(command[1])
            _getHandler(socket, client, key)

    elif(command[0].upper() == SET):
        if(len(command) < 5):
            _sendGuide(socket, client)
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
                _setHandler(socket,client, key, flag, exp, byte, value)
            except:
                _sendError(socket, client)
    else:
        _sendGuide(socket, client)



def _send(socket, client, data):
    socket.send_multipart([client,data])

def _sendGuide(socket, client):
    guide = "ERROR\r\nSUPPORTED OPERATIONS:\n-SET (SET <key> <flag> <exp> <byte> <data>)\n-GET (SET <key> <data>)\n\nBYE\n"
    _send(socket, client, guide)

def _sendError(socket, client):
    error = "ERROR\r\n"
    _send(socket, client, error)

def _setHandler(socket,client, key, flag, exp, byte, value):
    _send(socket, client, "ERROR\r\nSTILL NOT IMPLEMENTED\n" + str(key))

def _getHandler(socket, client, key):
    _send(socket, client, "ERROR\r\nSTILL NOT IMPLEMENTED\n" + str(key))

def hashOfKey(key):
    return crc32(key) % (1<<32)
