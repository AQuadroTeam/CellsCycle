#! /usr/bin/env python

class SettingsManager:

    def __init__(self):
         self.configDict = {}


    def readConfigurationFile(self, filePath):
        self.filePath = filePath
        with open(filePath, 'r') as f:
             for line in f:
                 splitLine = line.split()
                 self.configDict[splitLine[0]] = splitLine[1:]

             f.close()

    def printAllSettings(self):
        for (key,value) in self.configDict.iteritems() :
            print key,value
