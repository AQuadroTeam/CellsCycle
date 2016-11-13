from threading import Thread
import zmq
from Queue import Queue
from binascii import crc32
from CellCycle.MemoryModule.MemoryManagement import standardKillRequest, standardSlaveSetRequest, standardSlaveGetRequest, standardTransferRequest, standardMasterSetRequest, standardMasterGetRequest
from CellCycle.AWS.AWSlib import *

def startExtraCycleListeners(settings, logger, list_manager=None):
    threadNumber = settings.getServiceThreadNumber()
    port = settings.getClientEntrypointPort()

    logger.debug("list_manager received by ExtraCycle listeners : " + str(list_manager))

    # prepare socket urls
    url_Frontend = "tcp://*:" + str(port)

    # Prepare our context and sockets
    context = zmq.Context.instance()

    socket = context.socket(zmq.STREAM)
    socket.bind(url_Frontend)

    queue = Queue()

    for i in range(threadNumber):
        th = Thread(name='ServiceEntrypointThread',target=_serviceThread, args=(settings, logger, url_Frontend, socket, queue, list_manager))
        th.start()

    Thread(name='ServiceEntrypointRouterThread',target=_receiverThread, args=(logger, socket, queue)).start()


def _receiverThread(logger, socket, queue):
    while True:
        try:
            client, command = socket.recv_multipart()
            queue.put([client, command])
        except KeyboardInterrupt as e:
            logger.error(str(e))
            return

def _serviceThread(settings, logger, url_Backend,socket,queue, list_manager):
    logger.debug("Listening for clients on " + url_Backend)
    while True:
        try:
            client, message = queue.get()
        except KeyboardInterrupt as e:
            logger.error(str(e))
            return

        if(message != ""):
            command = message.split()
            try:
                logger.debug("Received command: " + str(command))
                _manageRequest(logger, settings, socket, command, client, list_manager)
            except Exception as e:
                logger.warning("Error for client: "+ str(client) +", error:"+ str(e) + ". command: " + message)


def _manageRequest(logger, settings, socket, command, client, list_manager):
    GET = "GET"
    ADD = "ADD"
    DELETE = "DELETE"
    SET = "SET"
    setList = [ADD , SET]
    QUIT = "QUIT"
    TRANSFER = "TRANSFER"
    CELLCYCLE = "CELLCYCLE"

    if(command[0].upper() == GET):
        if(command[1] != ""):
            key = hashOfKey(command[1])
            try:
                _getHandler(settings, socket, client, key, list_manager)
            except Exception as e:
                logger.warning(str(e) + " for command: " + " ".join(command))
                _sendError(socket, client)
            return;
        else:
            _sendGuide(socket, client)
            return;
    if(command[0].upper() == TRANSFER):
        _transferHandler(settings, socket, client)
        return;
    if(command[0].upper() == DELETE):
        if(command[1] != ""):
            key = hashOfKey(command[1])
            _deleteHandler(settings, socket, client, key, list_manager)
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
                _setHandler(settings, socket,client, key, flag, exp, byte, value, list_manager)
            except Exception as e:
                logger.warning(str(e) + " for command: " + " ".join(command))
                _sendError(socket, client)

            return
    elif(command[0].upper() == QUIT):
        _quitHandler(settings, socket, client)
        return
    elif(command[0].upper() == CELLCYCLE):
        if (len(command) < 2):
            _sendGuide(socket, client)
            return
        KILLYOURSELF = "KILLYOURSELF"
        NEWCELL = "NEWCELL"
        LOG = "LOG"

        operation = command[1]
        params = " ".join(command[2:])

        if(operation.upper() == KILLYOURSELF):
            TERMINATE = "TERMINATE"
            STOP = "STOP"
            logger.debug("Hello darkness my old friend...")
            if(params.upper() == STOP):
                _awsKillYourselfStopHandler(settings, logger, socket, client)
                return
            elif(params.upper() == TERMINATE):
                _awsKillYourselfTerminateHandler(settings, logger, socket, client)
                return
            else:
                _sendGuide(socket, client)
                return
        elif(operation.upper() == NEWCELL):
            logger.debug("I'm creating a new node on AWS with params: " + str(params))
            _awsCreateCellHandler(settings,logger, socket, client,  params )
            return
        elif(operation.upper() == LOG):
            _log(settings, logger, socket, client)
            return

        else:
            _sendGuide(socket, client)
            return


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
        "-GET (GET <key>)\n"\
        "-DELETE (DELETE <key> <data>)\n"\
        "-CELLCYCLE \n"\
        "\tKILLYOURSELF <TERMINATE or STOP>\n"\
        "\tNEWCELL <params>\n"\
        "\tLOG\n"\
        "\nBYE\r\n"
    _send(socket, client, guide)

def _sendError(socket, client):
    error = "ERROR\r\n"
    _send(socket, client, error)

def _setHandler(settings, socket,client, key, flag, exp, byte, value, list_manager):
    #add flag to stored data
    value = '{:010d}'.format(int(flag)) + value
    # TODO check this line
    host = list_manager.node_list.find_memory_key(key)
    #get server node
    #hosts = getNodesForKey(key)
    returnValue =standardMasterSetRequest(settings, key, value, host.target.ip)
    # TODO commented this line
    # returnValue = standardMasterSetRequest(settings, key, value)

    returnString = "STORED\r\n"
    _send(socket, client, returnString)

def _deleteHandler(settings, socket,client, key, list_manager):
    #TODO check this line
    host = list_manager.node_list.find_memory_key(key)
    #get server node
    #hosts = getNodesForKey(key)
    returnValue =standardMasterGetRequest(settings, key, host.target.ip)
    # TODO commented this line
    # returnValue = standardMasterSetRequest(settings, key, None)
    returnString = "DELETED\r\n"
    _send(socket, client, returnString)


def _getHandler(settings, socket, client, key, list_manager):
    #TODO host = list_manager.get_ip_for_key(key)
    #get server nodes and choose
    host = list_manager.node_list.find_memory_key(key)
    if(random()>0.5):
       returnValue =standardMasterGetRequest(settings, key, host.target.ip)
    else:
       returnValue =standardSlaveGetRequest(settings, key, host.target.ip)
    #
    # TODO replace else ip with slave ip
    #returnValue = standardMasterGetRequest(settings, key)
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

def _transferHandler(settings, socket, client):
    _send(socket, client, "DOING....")
    standardTransferRequest(settings)
    _send(socket, client, "DONE!\r\n")

def _awsCreateCellHandler(settings,logger,  socket, client,  params ):
    _send(socket, client, "SENDING REQUEST TO AMAZON\r\n")
    startInstanceAWS(settings, logger, params)

def _log(settings,logger,  socket, client):
    from CellCycle.Logger.Logger import getAllLog
    _send(socket, client, str(getAllLog(settings))+"\nEND OF LOG\r\n")

def _awsKillYourselfStopHandler(settings,logger, socket, client):
    _send(socket, client, "HELLO DARKNESS MY OLD FRIEND...\r\n")
    stopThisInstanceAWS(settings, logger)

def _awsKillYourselfTerminateHandler(settings,logger, socket, client):
    _send(socket, client, "HELLO DARKNESS MY OLD FRIEND...\r\n")
    terminateThisInstanceAWS(settings, logger)


def hashOfKey(key):
    return crc32(key) % (1<<32)
