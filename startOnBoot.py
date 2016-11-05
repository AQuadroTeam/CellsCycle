#!/home/ubuntu/git/CellsCycle/
import sys
from json import loads
serializedParams = sys.argv[1]
print serializedParams
params = loads(serializedParams)
import start
start.startApplication(params)
