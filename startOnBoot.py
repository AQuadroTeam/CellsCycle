#!/home/ubuntu/git/CellsCycle/
import sys
from json import loads
import start

serializedParams = sys.argv[1]
print serializedParams
params = loads(serializedParams)
start.startApplication(params)
