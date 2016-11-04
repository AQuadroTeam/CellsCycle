import boto3
# Let's use Amazon EC2
ec2 = boto3.resource('ec2')

imageIdCellCycle = 'ami-d27880bd'
instanceName = 'provaNome'
ec2.create_instances(ImageId=imageIdCellCycle, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=instanceName)
