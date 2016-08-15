#! /usr/bin/env python
from CellCycle.SettingsReader.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper

SETTINGSFILEPATH = "./config.txt"

# read settings from config.txt
settings = SettingsManager().readConfigurationFromFile(SETTINGSFILEPATH)

# setup logger. to write messages: logger.warning("hello warning"), logger.exception(""), logger.debug("Hi,I'm a bug")
logger = LoggerHelper(settings).logger
