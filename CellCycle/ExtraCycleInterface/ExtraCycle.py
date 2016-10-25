from threading import Thread
import zmq
from Queue import Queue

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

    _receiverThread(logger, socket, queue)


def _receiverThread(logger, socket, queue):
    while True:
        print "in ascolto"
        client, command = socket.recv_multipart()
        print "ho ricevuto "+ command
        queue.put([client, command])


def _serviceThread(logger, url_Backend,socket,queue):
    logger.debug("Listening for clients on " + url_Backend)
    while True:
        client, message = queue.get()
        logger.debug( "received service command: " + str(message))
        import time #simulate process I have to parse message, read code, generate hash, ask for node and send request
        time.sleep(5)
        socket.send_multipart([client,"super ciao!"])
