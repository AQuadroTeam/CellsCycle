# This is a test for Internal and External Channels
from CellCycle.ChainModule.ListCommunication import *
from zmq import ZMQError, Again
from time import sleep
from CellCycle.ChainModule.Message import Message
from CellCycle.ChainModule.Const import *
from cPickle import loads, dumps
from multiprocessing import Process

from start import loadSettings, loadLogger


def client_behavior(settings, logger):

    internal_channel = InternalChannel(addr="127.0.0.1", port=settings.getIntPort(), logger=logger)

    try:
        internal_channel.generate_internal_channel_client_side()
    except ZMQError as e:
        logger.debug(e)

    message = Message()
    message.priority = ALIVE
    message.source_flag = INT
    message.source_id = '1'
    message.target_id = '1'
    message.target_addr = '192.168.1.1'
    message.target_key = '{}:{}'.format(0, 19)

    internal_channel.send_first_internal_channel_message(dumps(message))

    msg = internal_channel.wait_int_message(dont_wait=False)

    logger.debug("msg : " + msg)

    external_channel = ExternalChannel(addr="127.0.0.1", port=settings.getExtPort(), logger=logger)
    external_channel.generate_external_channel_client_side()
    external_channel.external_channel_subscribe()

    logger.debug(loads(external_channel.wait_ext_message()).printable_message())

    logger.debug("try_to_connect TEST COMPLETED")

    stop = False
    while not stop:
        try:
            logger.debug(loads(external_channel.wait_ext_message()).printable_message())
            sleep(1)
        except Again:
            logger.debug("my master is DEAD")
            stop = True


def server_behavior(settings, logger):

    internal_channel = InternalChannel(addr="127.0.0.1", port=settings.getIntPort(), logger=logger)

    try:
        internal_channel.generate_internal_channel_server_side()
        msg = loads(internal_channel.wait_int_message(dont_wait=False))
        logger.debug("msg : ")
        logger.debug(msg.printable_message())
        internal_channel.reply_to_int_message(OK)
    except ZMQError as e:
        logger.debug(e)

    external_channel = ExternalChannel(addr="127.0.0.1", port=settings.getExtPort(), logger=logger)

    external_channel.generate_external_channel_server_side()
    external_channel.external_channel_publish()

    message = Message()
    message.priority = ALIVE
    message.source_flag = EXT
    message.source_id = '1'
    message.target_id = '1'
    message.target_addr = '192.168.1.1'
    message.target_key = '{}:{}'.format(0, 19)

    sleep(1)

    external_channel.forward(dumps(message))

    logger.debug("try_to_connect TEST COMPLETED")

    stop = False
    while not stop:
        try:
            external_channel.forward(dumps(message))
            sleep(1)
        except zmq.Again:
            stop = True

CONFIG_PATH = "/home/alessandro/git/CellsCycle/config.txt"

loaded_settings = loadSettings()
loaded_logger = loadLogger(settings=loaded_settings)

reader = Process(name='Reader', target=client_behavior, args=[loaded_settings, loaded_logger])
writer = Process(name='Writer', target=server_behavior, args=[loaded_settings, loaded_logger])

reader.start()
sleep(3)
writer.start()

sleep(5)
reader.terminate()
