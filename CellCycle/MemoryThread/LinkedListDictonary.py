# Linked List Utils - LIFO
# Tagged Linked List, useful to maintain original values and link them at the same moment through different Double Linked Lists
#Interface required:
#
#   Linked List class must have these dictonary entries:
#   - lists["tag" + "head"] = (head node linker)
#   - lists["tag" + "tail"] (tail node linker)
#
#   Node class must have these dictonary entries:
#   - pointer["tag" + "prev"] =  (previous node linker)
#   - pointer["tag" + "next"] =  (next node linker)
#   - pointer["tag" + "index"] =  (index of this list)
#   Node class must have methods (for debug):
#   __int__(self)
#

# With the same instances, you could organize different Double Linked List, one for each chosen tag.
# Example:
# Nodes are just 5. Class of these object is not important. It's necessary that this class has as parameter a dictonary called "pointer"
# We can ipotize that these elements are cars. A car has these parameters: gasoline level (0,100) and speed (0,120)
# This tool can organize these 5 objects in a double linked list sorted by ascending gasoline level and a double linked list sorted by ascending speed at the same time.
#
#

def getHeadAndTail(ll, tag):
    return getHead(ll,tag), getTail(ll,tag)

def isEmpty(ll, tag):
    head, tail = getHeadAndTail(ll, tag)
    return True if tail == None and head == None else False

def hasOneElement(ll, tag):
    head, tail = getHeadAndTail(ll, tag)
    return True if tail == head else False

def getTail(ll, tag):
    return ll.lists[tag + "tail"]

def setTail(ll, tag, node):
    ll.lists[tag + "tail"] = node

def getHead(ll, tag):
    return ll.lists[tag + "head"]

def setHead(ll, tag, node):
    ll.lists[tag + "head"] = node

def setHeadAndTail(ll, tag, head, tail):
    setHead(ll, tag, head)
    setTail(ll, tag, tail)

def getNext(tag, node):
    return node.pointer[tag + "next"]

def setNext(tag, node, next):
    node.pointer[tag + "next"] = next

def getPrev(tag, node):
    return node.pointer[tag + "prev"]

def setPrev(tag, node, prev):
    node.pointer[tag + "prev"] = prev

def getIndex(tag, node):
    return node.pointer[tag + "index"]

def setIndex(tag, node, index):
    node.pointer[tag + "index"] = index

def getPrevAndNext(tag, node):
    return getPrev(tag, node), getNext(tag, node)

def setPrevAndNext(tag, node, prev, next):
    setPrev(tag, node, prev)
    setNext(tag, node, next)

def push(ll,tag, newnode):
    if isEmpty(ll, tag):
        setTail(ll,tag, newnode)
        setHead(ll,tag, newnode)
        setNext(tag, newnode, None)
        setPrev(tag, newnode, None)
        return


    tail = getTail(ll, tag)

    #update tail
    setTail(ll, tag, newnode)
    #update link of newnode node
    setPrevAndNext(tag, newnode, tail, None )
    #update link of old tail
    setNext(tag, tail, newnode)



def pop(ll, tag, node=None):
    node = node if node != None else getTail(ll, tag)

    # empty list
    if isEmpty(ll, tag):
        return None

    # 1 object in list
    if hasOneElement(ll, tag):
        old = getHead(ll, tag)
        setHeadAndTail(ll, tag, None, None)
        return old

    head, tail = getHeadAndTail(ll, tag)
    prev = getPrev(tag, node)
    next = getNext(tag, node)
    if node == head:
        setHead(ll, tag, next)
    else:
        setNext(tag, prev, next)
    if node == tail:
        setTail(ll, tag, newtail)
    else:
        setPrev(tag, next, prev)

    setPrevAndNext(tag,node, None, None)

    return node

def increment(ll, tag, node):
    switch(ll,tag,getPrev(tag, node) , node )

#switch consecutive objects
def switch(ll,tag, before, after):
    if isEmpty(ll,tag) or hasOneElement(ll,tag):
        return

    # after is the head
    if before == None:
        return

    if getHead(ll,tag) == before:
        setHead(ll, tag, after)
    else:
        setNext(tag, getPrev(tag, before), after)

    if getTail(ll, tag) == after:
        setTail(ll, tag, before)
    else:
        setPrev(tag, getNext(tag, after), before)

    setNext(tag, before, getNext(tag, after))
    setPrev(tag, after, getPrev(tag, before))

    setPrev(tag, before, after)
    setNext(tag, after, before)

    return


def lastsWillBeFirsts(ll, tag):
    if isEmpty(ll, tag) or hasOneElement(ll,tag):
        return

    bringToFirst(ll,tag, getTail(ll, tag))


def bringToFirst(ll, tag, node):
    if isEmpty(ll,tag) or hasOneElement(ll,tag):
        return

    oldtail = getTail(ll,tag)
    oldhead = getHead(ll, tag)
    newhead = node

    if oldhead == node:
        return

    # update tail if necessary
    if oldtail == node:
        newtail = getPrev(tag, oldtail)
        setTail(ll,tag, newtail)
        setNext(tag, newtail, None)
    else:
        setPrev(tag, getNext(tag, node), getPrev(tag, newhead))

    setHead(ll, tag, newhead)

    setNext(tag, getPrev(tag, newhead), getNext(tag, newhead))

    #update new head
    setPrevAndNext(tag, newhead, None, oldhead)
    setPrev(tag, oldhead, newhead)

def nodeIndex(tag, node ):
    if node != None:
        return str(int(getIndex(tag, node)))
    else:
        return "NN"

def nodeIndexPlus(tag, node):
    return nodeIndex(tag, node)+"("+ nodeIndex(tag,getPrev(tag, node))+","+nodeIndex(tag,getNext(tag, node)) +")"

def listToString(ll, tag):
    if isEmpty(ll, tag):
        return "LL: Empty list"
    if hasOneElement(ll, tag):
        return "LL 1 elment: " + nodeIndexPlus(tag,getHead(ll, tag))

    string = "LL"+ "("+ nodeIndex(tag, getHead(ll, tag)) + "," + nodeIndex(tag, getTail(ll, tag)) + ")"+": "
    node = getHead(ll, tag)
    it = 0
    while node != None and it < 20:
        string += nodeIndexPlus(tag,node) + "-"
        node = getNext(tag, node)
        it += 1
    return string

def printList(ll, tag):
    print listToString(ll ,tag)

class LinkedList:
    def __init__(self,tag):
        self.lists = {}
        self.lists[tag + "head"] = None
        self.lists[tag + "tail"] = None

class Node:
    def __init(self,tag,  index, data = None):
        self.pointer = {}
        self.pointer[tag + "next"] = None
        self.pointer[tag + "prev"] = None
        self.data = data
        self.index = index

    def __int__(self):
        return str(self.index)
