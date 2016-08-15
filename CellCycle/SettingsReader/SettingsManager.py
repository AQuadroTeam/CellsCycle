#! /usr/bin/env python
from SettingsObject import SettingsObject

class SettingsManager:

    def __init__(self):
         self.configDict = {}

    def readConfigurationFromFile(self, filePath):
        self.filePath = filePath
        # this dict will initialize SettingObject
        dict = {}

        with open(filePath, 'r') as f:
             for line in f:
                 splitLine = line.split()
                 dict[splitLine[0]] = splitLine[1:]

             f.close()

        # create new SettingsObject
        return SettingsObject(dict)
