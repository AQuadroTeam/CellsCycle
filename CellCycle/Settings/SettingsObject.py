# All info at https://github.com/AQuadroTeam/CellsCycle/wiki/Settings
import Constants

def manualSettings(logFile=None, verbose=False, preallocatedPool=100, slabSize=10, getterThreadNumber=1 , MasterSetPort=5550, MasterGetPort=5551, SlaveSetPort=5552, SlaveGetPort=5553, intPort=5193, extPort=5194, memoryObjectPort=5559):
    dic = {}
    dic[Constants.LOGFILE] = [logFile]
    dic[Constants.VERBOSE] =  [verbose]
    dic[Constants.SLABSIZE] = [slabSize]
    dic[Constants.PREALLOCATEDPOOL] = [preallocatedPool]
    dic[Constants.GETTERTHREADNUMBER] = [getterThreadNumber]
    dic[Constants.MASTERSETPORT] = [MasterSetPort]
    dic[Constants.MASTERGETPORT] = [MasterGetPort]
    dic[Constants.SLAVESETPORT] = [SlaveSetPort]
    dic[Constants.SLAVEGETPORT] = [SlaveGetPort]
    dic[Constants.INTPORT] = [intPort]
    dic[Constants.EXTPORT] = [extPort]
    dic[Constants.MEMORYOBJECTPORT] = [memoryObjectPort]

    return SettingsObject(dic)


class SettingsObject(object):

    def __init__(self, dict = None, deserialize=None):
        self.configDict = dict
        if(deserialize != None):
            import json
            self.configDict = json.loads(deserialize)

    def serialize(self):
        import json
        return json.dumps(self.configDict)


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

    def getValueMaxSize(self):
        return int(self.configDict[Constants.VALUEMAXSIZE][0])
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

    def getIntPort(self):
        return int(self.configDict[Constants.INTPORT][0])

    def getExtPort(self):
        return int(self.configDict[Constants.EXTPORT][0])

    def getMinInstance(self):
        return int(self.configDict[Constants.MININSTANCE][0])

    def getMaxInstance(self):
        return int(self.configDict[Constants.MAXINSTANCE][0])

    def getMemoryObjectPort(self):
        return int(self.configDict[Constants.MEMORYOBJECTPORT][0])

    # end of network settings

    # client entrypoint service settings
    def getServiceThreadNumber(self):
        return int(self.configDict[Constants.SERVICETHREADNUMBER][0])

    def getClientEntrypointPort(self):
        return int(self.configDict[Constants.CLIENTENTRYPOINTPORT][0])
    # end of client entrypoint service settings
    #

    # metric settings
    def getScalePeriod(self):
        return int(self.configDict[Constants.SCALEPERIOD][0])
    def getGetScaleUpLevel(self):
        return float(self.configDict[Constants.GETSCALEUPLEVEL][0])
    def getGetScaleDownLevel(self):
        return float(self.configDict[Constants.GETSCALEDOWNLEVEL][0])
    def getSetScaleUpLevel(self):
        return float(self.configDict[Constants.SETSCALEUPLEVEL][0])
    def getSetScaleDownLevel(self):
        return float(self.configDict[Constants.SETSCALEDOWNLEVEL][0])
    # end of metric settings

    # aws settings
    def getAwsImageId(self):
        return str(self.configDict[Constants.AWSIMAGEID][0])
    def getAwsSecurityGroup(self):
        return str(self.configDict[Constants.AWSSECURITYGROUP][0])
    def getAwsKeyName(self):
        return str(self.configDict[Constants.AWSKEYNAME][0])
    def setAwsKeyName(self,key):
        self.configDict[Constants.AWSKEYNAME][0] = str(key)
    def getGitBranch(self):
        return str(self.configDict[Constants.GITBRANCH][0])
    def setGitBranch(self, branch):
        self.configDict[Constants.GITBRANCH][0] = branch
    def getAwsStartFile(self):
        return str(self.configDict[Constants.STARTFILE][0])
    def getAwsProfileName(self):
        return str(self.configDict[Constants.AWSPROFILENAME][0])
    def setAwsProfileName(self, name):
        self.configDict[Constants.AWSPROFILENAME][0] = str(name)
    def getAWSType(self):
        return str(self.configDict[Constants.AWSTYPE][0])
    # end of aws settings

    def __str__(self):
        string = "Configuration:\n"
        for (key,value) in self.configDict.iteritems() :
            string += key + " : " + str(value) + "\n"
        string += "End Of Configuration\n"
        return string



    def printAll(self):
        print self
