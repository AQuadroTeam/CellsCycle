# This is a test for Internal and External Channels
from CellCycle.ChainModule.ListCommunication import *
from start import loadSettingsAndLogger
from zmq import ZMQError
from threading import Thread
from time import sleep
from CellCycle.ChainModule.Message import Message
from CellCycle.ChainModule.Const import *
from cPickle import loads, dumps


def client_behavior(settings, logger):

    internal_channel = InternalChannel(addr="127.0.0.1", port=settings.getIntPort(), logger=logger)

    try:
        internal_channel.generate_internal_channel_client_side()
    except ZMQError as e:
        logger.debug(e)

    message = Message()
    message.priority = ALIVE
    message.source_flag = EXT
    message.source_id = '1'
    message.target_id = '1'
    message.target_addr = '192.168.1.1'
    message.target_key = '{}:{}'.format(0, 19)

    internal_channel.send_first_internal_channel_message(dumps(message))

    msg = internal_channel.wait_int_message(dont_wait=False)

    logger.debug("msg : " + msg)

    logger.debug("try_to_connect without server TEST COMPLETED")


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

    logger.debug("try_to_connect without server TEST COMPLETED")

CONFIG_PATH = "/home/alessandro/git/CellsCycle/config.txt"

loaded_settings, loaded_logger = loadSettingsAndLogger(CONFIG_PATH)

reader = Thread(name='Reader', target=client_behavior, args=[loaded_settings, loaded_logger])
writer = Thread(name='Writer', target=server_behavior, args=[loaded_settings, loaded_logger])

reader.start()
sleep(3)
writer.start()
