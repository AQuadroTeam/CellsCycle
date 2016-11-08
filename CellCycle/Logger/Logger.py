# read configuration from config file
import logging
import sys
import traceback
# From Logging Python Documentation :  This function should be called from the main thread before
# other threads are started. In versions of Python prior to 2.7.1 and 3.2, if this function is called from multiple threads,
# it is possible (in rare circumstances) that a handler will be added to the root logger more than once,
# leading to unexpected results such as messages being duplicated in the log.

# logging is threadsafe, concurrency is managed between threads

class LoggerHelper:

    def __init__(self, settings):
        self.logFilePath = settings.getLogFile()
        self.verbosity = settings.isVerbose()

        # this function setups stdout logger and file logger, it's needed!
        self.logger = self.setupLogger()

    def setupLogger(self):

        # get a logger
        logger = logging.getLogger()

        # level of the getter, DEBUG is (almost) the lowest, to filter messages use ERROR
        logger.setLevel(logging.DEBUG)

        # format of log lines
        formatter = logging.Formatter('%(asctime)s %(threadName)s %(processName)s %(levelname)s: %(message)s')

        # build log handler for logFile
        fl = logging.FileHandler(self.logFilePath)
        fl.setLevel(logging.DEBUG)
        fl.setFormatter(formatter)

        # install handler
        logger.addHandler(fl)

        if (self.verbosity):
            # build stderr handler if desired
            ch = logging.StreamHandler(sys.stderr)
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        # Configure logger to write to an Uncaught throwable...
        def my_handler(type, value, tb):
            logger.exception("Uncaught " + str(type) + " : " +str(value)+ " @ " + str(traceback.format_tb(tb) ) )
        # Install exception handler
        sys.excepthook = my_handler

        return logger

def getAllLog(settings):
    file = open(settings.getLogFile(), "r")
    log = file.read()
    file.close()
    return log
