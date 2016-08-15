import Constants

class SettingsObject:

    def __init__(self, dict):
        self.configDict = dict

    def getLogFile(self):
        return self.configDict[Constants.LOGFILE][0]

    def isVerbose(self):
        return True if self.configDict[Constants.VERBOSE][0] == "True" else False



    def __str__(self):
        string = "Configuration:\n"
        for (key,value) in self.configDict.iteritems() :
            string += key + " : " + str(value) + "\n"
        string += "End Of Configuration\n"
        return string

    def printAll(self):
        print self
