#! /usr/bin/env python
from CellCycle.SettingsReader.SettingsManager import SettingsManager
from CellCycle.Logger.Logger import LoggerHelper

SETTINGSFILEPATH = "./config.txt"

# read settings from config.txt
settings = SettingsManager().readConfigurationFromFile(SETTINGSFILEPATH)
logger = LoggerHelper(settings)
