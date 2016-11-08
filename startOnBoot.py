#!/home/ubuntu/git/CellsCycle/
import sys
import start
from json import loads
from CellCycle.Settings.SettingsObject import SettingsObject

serializedParams = sys.argv[1]
serializedSettings = sys.argv[2]

params = loads(serializedParams)
settings = SettingsObject(deserialize=serializedSettings)

start.startApplication(params, settings)
