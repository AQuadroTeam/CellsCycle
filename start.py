#! /usr/bin/env python
from CellCycle.SettingsReader.SettingsReader import SettingsReader


settings = SettingsReader()
settings.readConfigurationFile()
settings.printAllSettings()
