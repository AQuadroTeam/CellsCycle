import boto3

def startInstanceAWS(settings, logger):
    logger.debug("contact amazon")
    ec2 = boto3.resource('ec2')

    imageIdCellCycle = settings.getAwsImageId()
    keyName = settings.getAwsKeyName()
    branch = settings.getGitBranch()
    securityGroup = settings.getAwsSecurityGroup()
    userData = "#!/bin/bash\nsu ubuntu\ncd /home/ubuntu/git/CellsCycle/\ngit checkout "+branch+"\ngit pull origin "+branch+"\n/usr/bin/python startOnBoot.py\nADDRESSOFFATHER=prova"

    logger.debug("id image: " + imageIdCellCycle)
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
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=instanceID).terminate()

def stopInstanceAWS(settings, logger, instanceID):
    logger.debug("contact amazon to stop : " + instanceID)
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=instanceID).stop()
