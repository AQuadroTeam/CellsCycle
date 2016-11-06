# This is a test for Internal and External Channels
from CellCycle.ChainModule.ListCommunication import *
from start import loadSettingsAndLogger
from zmq import ZMQError
from threading import Thread
from time import sleep


def client_behavior(settings, logger):

    internal_channel = InternalChannel(addr="127.0.0.1", port=settings.getIntPort(), logger=logger)

    try:
        internal_channel.generate_internal_channel_client_side()
    except ZMQError as e:
        logger.debug(e)

    internal_channel.send_first_internal_channel_message(message=OK)

    msg = internal_channel.wait_int_message(dont_wait=False)

    logger.debug("msg : " + msg)

    logger.debug("try_to_connect without server TEST COMPLETED")


def server_behavior(settings, logger):

    internal_channel = InternalChannel(addr="127.0.0.1", port=settings.getIntPort(), logger=logger)

    try:
        internal_channel.generate_internal_channel_server_side()
        msg = internal_channel.wait_int_message(dont_wait=False)
        logger.debug("msg : " + msg)
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
