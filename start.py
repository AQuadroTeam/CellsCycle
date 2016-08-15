#! /usr/bin/env python
from CellCycle.SettingsReader.SettingsManager import SettingsManager

SETTINGSFILEPATH = "./config.txt"

# read settings from config.txt
settings = SettingsManager()
settings.readConfigurationFile(SETTINGSFILEPATH)
settings.printAllSettings()
