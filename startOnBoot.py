#!/usr/bin/python
with open("/home/ubuntu/git/CellsCycle/log.txt", "a") as myfile:
    myfile.write("booted\n")
import start
start.startApplication()
