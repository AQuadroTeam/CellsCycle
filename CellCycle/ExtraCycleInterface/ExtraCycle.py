from threading import Thread
import zmq

def startExtraCycleListeners(settings, logger):
    threadNumber = settings.getServiceThreadNumber()
    port = settings.getClientEntrypointPort()

    # prepare socket urls
    url_Backend = "inproc://EntrypointService"
    url_Frontend = "tcp://*:" + str(port)

    # Prepare our context and sockets
    context = zmq.Context.instance()

    # Socket to talk to get
    socketFrontend = context.socket(zmq.ROUTER)
    socketFrontend.bind(url_Frontend)

    # Socket to talk to workers
    socketGetBackend = context.socket(zmq.DEALER)
    socketGetBackend.bind(url_Backend)


    Thread(name='ExtraCycleCommunicationProxy',target=_proxyThread, args=(logger, master, socketFrontend, socketBackend, url_Frontend, url_Backend)).start()

    for _ in range(getterNumber):
        th = Thread(name='ServiceEntrypointThread',target=_serviceThread, args=(logger, url_Backend))
        th.start()


def _serviceThread(logger, url_Backend):
    logger.debug("Listening for clients on " + url)
    context = zmq.Context.instance()
    socket = context.socket(zmq.STREAM)
    socket.connect(url)

    while True:
        command = loads(socket.recv())
        logger.debug( "received service command: " + str(command))
        



def _proxyThread(logger, master, frontend, backend, url_frontend, url_backend):
    logger.debug("Routing from " + url_frontend + " to " + url_backend)
    zmq.proxy(frontend, backend)
