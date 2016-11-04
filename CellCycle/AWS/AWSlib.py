import boto3

def startInstanceAWS(settings, logger):
    logger.debug("contact amazon")
    ec2 = boto3.resource('ec2')

    imageIdCellCycle = settings.getAwsImageId()
    logger.debug("id image: " + imageIdCellCycle)
    ec2.create_instances(ImageId=imageIdCellCycle, MinCount=1, MaxCount=1, InstanceType='t2.micro')

def terminateInstanceAWS(settings, logger, instanceID):
    logger.debug("contact amazon to terminate : " + instanceID)
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=instanceID).terminate()

def stopInstanceAWS(settings, logger, instanceID):
    logger.debug("contact amazon to stop : " + instanceID)
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=instanceID).stop()
