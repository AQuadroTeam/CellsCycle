# All info at https://github.com/AQuadroTeam/CellsCycle/wiki/Settings
import Constants

class SettingsObject:

    def __init__(self, dict):
        self.configDict = dict

    def getLogFile(self):
        return self.configDict[Constants.LOGFILE][0]

    def isVerbose(self):
        return True if self.configDict[Constants.VERBOSE][0] == "True" else False

    def getSlabSize(self):
        return int(self.configDict[Constants.SLABSIZE][0])

    def getPreallocatedPool(self):
        return int(self.configDict[Constants.PREALLOCATEDPOOL][0])

    def __str__(self):
        string = "Configuration:\n"
        for (key,value) in self.configDict.iteritems() :
            string += key + " : " + str(value) + "\n"
        string += "End Of Configuration\n"
        return string

    def printAll(self):
        print self
