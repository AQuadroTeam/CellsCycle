from threading import Thread
import zmq
from Queue import Queue
from binascii import crc32
from CellCycle.MemoryModule.MemoryManagement import standardKillRequest, standardSlaveSetRequest, standardSlaveGetRequest, standardTransferRequest, standardMasterSetRequest, standardMasterGetRequest
from CellCycle.AWS.AWSlib import *

def startExtraCycleListeners(settings, logger, list_manager=None):
    threadNumber = settings.getServiceThreadNumber()
    port = settings.getClientEntrypointPort()

    logger.debug("list_manager : " + str(list_manager))

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
        except Exception as e:
            logger.error(str(e))
            import traceback
            logger.error(traceback.format_exc())


def _serviceThread(settings, logger, url_Backend,socket,queue, list_manager):
    logger.debug("Listening for clients on " + url_Backend)
    while True:
        try:
            client, message = queue.get()
            if(message != "" and message!="\n"):
                command = message.split()

                if(settings.isVerbose()):
                    logger.debug("Received command: " + str(command))
                _manageRequest(logger, settings, socket, command, client, list_manager)

        except Exception as e:
            logger.error(str(e))
            import traceback
            logger.error(traceback.format_exc())




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
                _getHandler(settings, logger, socket, client, key, list_manager)
            except Exception as e:
                import traceback
                logger.warning("for command: " + " ".join(command) + " , error: " + str(traceback.format_exc()))
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
            _deleteHandler(settings,logger, socket, client, key, list_manager)
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
                import traceback
                logger.warning("for command: " + " ".join(command) + " , error: " + str(traceback.format_exc()))
                _sendGuide(socket, client)
                return

            try:
                _setHandler(settings, logger, socket,client, key, flag, exp, byte, value, list_manager)
            except Exception as e:
                import traceback
                logger.warning("for command: " + " ".join(command) + " , error: " + str(traceback.format_exc()))
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
        KILLALL = "KILLALL"
        NEWCELL = "NEWCELL"
        SCALEUP = "SCALEUP"
        SCALEDOWN = "SCALEDOWN"
        LOG = "LOG"
        WHOHAS = "WHOHAS"
        KEYS = "KEYS"

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
        elif(operation.upper() == KILLALL):
            TERMINATE = "TERMINATE"
            STOP = "STOP"
            logger.debug("Hello darkness my old friend...")

            if(params.upper() == STOP):
                _awsKillAllStopHandler(settings, logger, socket, client)
                return
            elif(params.upper() == TERMINATE):
                _awsKillAllTerminateHandler(settings, logger, socket, client)
                return
            else:
                _sendGuide(socket, client)
                return

        elif(operation.upper() == NEWCELL):
            logger.debug("I'm creating a new node on AWS with params: " + str(params))
            _awsCreateCellHandler(settings,logger, socket, client,  params )
            return
        elif(operation.upper() == SCALEUP):
            logger.debug("Requests for scale Up!")
            # from CellCycle.ChainModule.ListThread import ListThread
            # from CellCycle.ChainModule.ListCommunication import InternalChannel
            # this channel is necessary to send scale up/down requests

            # internal_channel = InternalChannel(addr='127.0.0.1', port=settings.getIntPort(), logger=logger)
            # internal_channel.generate_internal_channel_client_side()
            logger.debug("I'm sending the scale up request...")
            # call scale up service
            # ListThread.notify_scale_up(internal_channel)
            list_manager.no_network_scale_up()
            _send(socket, client, "SENDED")
            logger.debug("Requested!")
            return
        elif(operation.upper() == SCALEDOWN):
            logger.debug("Requests for scale Down!")
            from CellCycle.ChainModule.ListThread import ListThread
            from CellCycle.ChainModule.ListCommunication import InternalChannel
            # this channel is necessary to send scale up/down requests
            # internal_channel = InternalChannel(addr='127.0.0.1', port=settings.getIntPort(), logger=logger)
            # internal_channel.generate_internal_channel_client_side()
            # call scale up service
            # logger.debug("I'm sending the scale down request...")
            # ListThread.notify_scale_down(internal_channel)
            _send(socket, client, "SENDED")
            logger.debug("Requested!")
            return
        elif(operation.upper() == LOG):
            _log(settings, logger, socket, client)
            return
        elif(operation.upper() == WHOHAS):
            key = hashOfKey(params)
            _whoHasHandler(settings, logger, client, socket, key, list_manager)
            return
        elif(operation.upper() == KEYS):
            _keysHandler(settings, logger, client, socket,list_manager)
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
        "-DELETE (DELETE <key>)\n"\
        "-CELLCYCLE \n"\
        "\tKILLYOURSELF <TERMINATE or STOP>\n"\
        "\tKILLALL <TERMINATE or STOP>\n"\
        "\tNEWCELL <params>\n"\
        "\tSCALEUP\n"\
        "\tSCALEDOWN\n"\
        "\tWHOHAS <key>\n"\
        "\tKEYS\n"\
        "\tLOG\n"\
        "\nBYE\r\n"
    _send(socket, client, guide)

def _sendError(socket, client):
    error = "ERROR\r\n"
    try:
        _send(socket, client, error)
    except Exception as e:
        pass

def _setHandler(settings, logger, socket,client, key, flag, exp, byte, value, list_manager):
    #add flag to stored data
    value = '{:010d}'.format(int(flag)) + value
    # TODO check this line
    host = list_manager.node_list.find_memory_key(key)
    #get server node
    #hosts = getNodesForKey(key)
    if(settings.isVerbose()):
        logger.debug("sending set request to " + str(host.target.ip))
    returnValue =standardMasterSetRequest(settings, key, value, host.target.ip)
    # TODO commented this line
    # returnValue = standardMasterSetRequest(settings, key, value)

    returnString = "STORED\r\n"
    _send(socket, client, returnString)

def _deleteHandler(settings, logger, socket,client, key, list_manager):
    #TODO check this line
    host = list_manager.node_list.find_memory_key(key)
    #get server node
    #hosts = getNodesForKey(key)
    if(settings.isVerbose()):
        logger.debug("sending delete request to " + str(host.target.ip))
    returnValue =standardMasterSetRequest(settings, key,None, host.target.ip)
    # TODO commented this line
    # returnValue = standardMasterSetRequest(settings, key, None)
    returnString = "DELETED\r\n"
    _send(socket, client, returnString)


def _getHandler(settings,logger,  socket, client, key, list_manager):
    from random import random
    #get server nodes and choose
    masterHost = list_manager.node_list.find_memory_key(key)
    slaveHost = masterHost.slave
    if(random()>0.5):
        if(settings.isVerbose()):
            logger.debug("sending get request to master " + str(masterHost.target.ip))
        returnValue =standardMasterGetRequest(settings, key, masterHost.target.ip)
    else:
        if(settings.isVerbose()):
            logger.debug("sending get request to slave" + str(slaveHost.ip))
        returnValue =standardSlaveGetRequest(settings, key, slaveHost.ip)
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
    try:
        _send(socket, client, b'')
    except Exception as e:
        pass

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

def _awsKillAllStopHandler(settings,logger, socket, client):
    _send(socket, client, "HELLO DARKNESS MY OLD FRIEND...\r\n")
    stopAllAWS(settings, logger)

def _awsKillAllTerminateHandler(settings,logger, socket, client):
    _send(socket, client, "HELLO DARKNESS MY OLD FRIEND...\r\n")
    terminateAllAWS(settings, logger)

def _whoHasHandler(settings, logger, client, socket, key, list_manager):
    masterHost = list_manager.node_list.find_memory_key(key)
    _send(socket, client,"Key " + str(key) +" is assigned to: "+ str(masterHost.target.ip)+"\r\n")

def _keysHandler(settings, logger, client, socket,list_manager):
    _send(socket, client, list_manager.node_list.print_list()+"\r\n")


def hashOfKey(key):
    return crc32(key) % (1<<32)
