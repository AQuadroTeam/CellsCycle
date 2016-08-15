#! /usr/bin/env python
from CellCycle.SettingsReader.SettingsManager import SettingsManager


settings = SettingsManager()
settings.readConfigurationFile()
settings.printAllSettings()
