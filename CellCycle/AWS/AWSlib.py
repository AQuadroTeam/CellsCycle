import boto3

def startInstanceAWS(settings, logger, params, privateIp=None):
    logger.debug("contact amazon")

    awsProfileName = settings.getAwsProfileName()
    ec2 = boto3.Session(profile_name=awsProfileName).resource('ec2')

    imageIdCellCycle = settings.getAwsImageId()
    keyName = settings.getAwsKeyName()
    branch = settings.getGitBranch()
    securityGroup = settings.getAwsSecurityGroup()
    startFile = settings.getAwsStartFile()


    from json import dumps
    serializedParams = dumps(params)
    serializedSettings = settings.serialize()

    userData = "#!/bin/bash\n" \
    "sudo cp /home/ubuntu/.aws /root/ -r\n" \
    "cd /home/ubuntu/git/CellsCycle/\n" \
    "sudo echo BEGIN OF LOGFILE > "+settings.getLogFile()+"\n" \
    "sudo git checkout "+branch+"  >> "+settings.getLogFile()+" 2>&1\n" \
    "sudo git fetch --all >> "+settings.getLogFile()+" 2>&1\n" \
    "sudo git reset --hard origin/" + branch +" >> "+settings.getLogFile()+" 2>&1\n" \
    "sudo /usr/bin/python "+ startFile + " '" + serializedParams + "' '" + serializedSettings + " >> extremeLog.log 2>&1'\n"

    logger.debug("id image: " + imageIdCellCycle)
    if(privateIp != None):
        ec2.create_instances(ImageId=imageIdCellCycle, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=keyName, SecurityGroups=[securityGroup], UserData=userData,     PrivateIpAddress=privateIp)
    else:
        ec2.create_instances(ImageId=imageIdCellCycle, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=keyName, SecurityGroups=[securityGroup], UserData=userData)


def terminateThisInstanceAWS(settings, logger):
    import requests
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    instance_id = response.text
    terminateInstanceAWS(settings, logger, instance_id)

def stopThisInstanceAWS(settings, logger):
    import requests
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    instance_id = response.text
    stopInstanceAWS(settings, logger, instance_id)

def terminateInstanceAWS(settings, logger, instanceID):
    logger.debug("contact amazon to terminate : " + instanceID)
    awsProfileName = settings.getAwsProfileName()
    ec2 = boto3.Session(profile_name=awsProfileName).resource('ec2')
    ec2.instances.filter(InstanceIds=[instanceID]).terminate()

def stopInstanceAWS(settings, logger, instanceID):
    logger.debug("contact amazon to stop : " + instanceID)
    awsProfileName = settings.getAwsProfileName()
    ec2 = boto3.Session(profile_name=awsProfileName).resource('ec2')
    ec2.instances.filter(InstanceIds=[instanceID]).stop()

def stopAllAWS(settings, logger):
    logger.debug("contact amazon to stop all")
    awsProfileName = settings.getAwsProfileName()
    ec2 = boto3.Session(profile_name=awsProfileName).resource('ec2')
    ec2.instances.stop()

def terminateAllAWS(settings, logger):
    logger.debug("contact amazon to terminate all")
    awsProfileName = settings.getAwsProfileName()
    ec2 = boto3.Session(profile_name=awsProfileName).resource('ec2')
    ec2.instances.terminate()
