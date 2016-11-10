'''There are two standard behaviour for requester to name a new child, depends on name of the Slave node of the creator.
If the greater whole number of Slave id and Requester id are the same (e.g. 3.1 and 3.999 or 3.4 and 4):
	Name new node with float (Requester id + (Slave id - Requester id)/2 )
Else:
	Name new node with the greater whole number of Requester Id


This naming behaviour is needed to maintain the total order relationship between nodes,
other structures as P2P Chord use a PseudoRandom Generator to name new nodes,
and generate a new random number between two ids, using high value numbers,
hoping there wont be consecutive ids (this solution can be easily avoided with our method).
'''
def calculateSonId(masterId , slaveId):
    import math
    masterGreaterWholeNumber = math.ceil(masterId)
    if (masterGreaterWholeNumber == masterId):
        masterGreaterWholeNumber += 1

    slaveGreaterWholeNumber = math.ceil(slaveId)

    if(slaveId < masterId):
        return masterGreaterWholeNumber + 1

    if(masterGreaterWholeNumber == slaveGreaterWholeNumber ):
        return float(masterId + (slaveId - masterId)/2.0)
    else:
        return masterGreaterWholeNumber
