# All info at https://github.com/AQuadroTeam/CellsCycle/wiki/Settings
import Constants

def manualSettings(logFile=None, verbose=False, preallocatedPool=100, slabSize=10, getterThreadNumber=1 ):
    dic = {}
    dic[Constants.LOGFILE] = [logFile]
    dic[Constants.VERBOSE] =  [verbose]
    dic[Constants.SLABSIZE] = [slabSize]
    dic[Constants.PREALLOCATEDPOOL] = [preallocatedPool]
    dic[Constants.GETTERTHREADNUMBER] = [getterThreadNumber]
    return SettingsObject(dic)

class SettingsObject(object):

    def __init__(self, dict):
        self.configDict = dict

    # log settings
    def getLogFile(self):
        return self.configDict[Constants.LOGFILE][0]

    def isVerbose(self):
        return True if self.configDict[Constants.VERBOSE][0] == "True" else False
    # end of log settings

    # memory settings
    def getSlabSize(self):
        return int(self.configDict[Constants.SLABSIZE][0])

    def getPreallocatedPool(self):
        return int(self.configDict[Constants.PREALLOCATEDPOOL][0])

    def getGetterThreadNumber(self):
        return int(self.configDict[Constants.GETTERTHREADNUMBER][0])
    # end of memory settings

    # network settings
    def getMasterSetPort(self):
        return int(self.configDict[Constants.MASTERSETPORT][0])

    def getMasterGetPort(self):
        return int(self.configDict[Constants.MASTERGETPORT][0])

    def getSlaveSetPort(self):
        return int(self.configDict[Constants.SLAVESETPORT][0])

    def getSlaveGetPort(self):
        return int(self.configDict[Constants.SLAVEGETPORT][0])

    # end of network settings

    def __str__(self):
        string = "Configuration:\n"
        for (key,value) in self.configDict.iteritems() :
            string += key + " : " + str(value) + "\n"
        string += "End Of Configuration\n"
        return string



    def printAll(self):
        print self
