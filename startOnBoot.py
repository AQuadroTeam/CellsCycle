#!/home/ubuntu/git/CellsCycle/
import sys
from json import loads
import start

serializedParams = sys.argv[1]
currentProfile = {}
currentProfile["profile_name"] = sys.argv[2]
currentProfile["key_pair"] =  sys.argv[3]
print serializedParams
params = loads(serializedParams)
import start
start.startApplication(params, currentProfile)
