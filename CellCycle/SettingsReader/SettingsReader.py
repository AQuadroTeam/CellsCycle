#! /usr/bin/env python
FILE_PATH = "./config.txt"

class SettingsReader:

    def __init__(self):
         self.configDict = {}
         self.filePath = FILE_PATH


    def readConfigurationFile(self):
         with open(FILE_PATH, 'r') as f:
             for line in f:
                 splitLine = line.split()
                 self.configDict[splitLine[0]] = splitLine[1:]

    def printAllSettings(self):
        for (key,value) in self.configDict.iteritems() :
            print key,value
