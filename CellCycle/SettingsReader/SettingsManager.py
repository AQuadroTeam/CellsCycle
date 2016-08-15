#! /usr/bin/env python
from SettingsObject import SettingsObject

class SettingsManager:

    def __init__(self):
        self.settings = False

    def readConfigurationFromFile(self, filePath):
        self.filePath = filePath
        # this dict will initialize SettingObject
        dict = {}

        with open(filePath, 'r') as f:
             for line in f:
                 splitLine = line.split()
                 dict[splitLine[0]] = splitLine[1:]

             f.close()

        self.settings = SettingsObject(dict)
        # create new SettingsObject
        return self.settings

    def getCurrentSettings(self):
        if (not self.settings):
            raise Exception('Settings Are Not Initialized!\n Please execute readConfigurationFromFile()')

        return self.settings
