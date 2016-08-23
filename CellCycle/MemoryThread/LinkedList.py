# Linked List Utils - LIFO

#Interface required:
#
#   Linked List class must have attributes:
#   - lltail (tail node linker)
#   - llhead (head node linker)
#
#   Node class must have attributes:
#   - llprev (previous node linker)
#   - llnext (next node linker)
#   Node class must have methods (for debug):
#   __int__(self)
#

def isEmpty(ll):
    return True if ll.lltail == None and ll.llhead == None else False

def hasOneElement(ll):
    return True if ll.lltail == ll.llhead else False

def getTail(ll):
    return ll.lltail

def getHead(ll):
    return ll.llhead

def push(ll, new):
    if isEmpty(ll):
        ll.lltail = new
        ll.llhead = new
        new.llnext = None
        new.llprev = None

    tail = ll.lltail

    #update tail
    ll.lltail = new
    #update link of new node
    new.llprev = tail
    new.llnext = None
    #update link of old tail
    tail.llnext = new
    printList(ll)
    print "a " + 3


def pop(ll):
    # empty list
    if isEmpty(ll):
        return None

    oldtail = ll.lltail

    # 1 object in list
    if hasOneElement(ll):
        ll.lltail = None
        ll.llhead = None
        return oldtail

    # n objects in list
    newtail = oldtail.llprev
    newtail.llnext = None
    ll.lltail = newtail

    oldtail.llnext = None
    oldtail.llprev = None

    return oldtail

def increment(ll, node):
    switch(ll,node.llprev , node )

#switch consecutive objects
def switch(ll,before, after):
    if isEmpty(ll) or hasOneElement(ll):
        return

    # after is the head
    if before == None:
        return

    if ll.llhead == before:
        ll.llhead = after

    if ll.lltail == after:
        ll.lltail = before

    before.llprev.llnext = after
    after.llnext.llprev = before

    before.llnext = after.llnext
    after.llprev = before.llprev

    before.llprev = after
    after.llnext = before

    return


def lastsWillBeFirsts(ll):
    if isEmpty(ll) or hasOneElement(ll):
        return

    bringToFirst(ll, ll.lltail)


def bringToFirst(ll, node):
    if isEmpty(ll) or hasOneElement(ll):
        return

    oldtail = ll.lltail
    oldhead = ll.llhead

    if oldhead == node:
        return

    # update tail if necessary
    if oldtail == node:
        newtail = oldtail.llprev
        ll.lltail = newtail
        newtail.llnext = None

    newhead = node

    ll.llhead = newhead

    #update new head
    newhead.llnext = oldhead
    newhead.llprev = None
    oldhead.llprev = newhead



def listToString(ll):
    if isEmpty(ll):
        return "LL: Empty list"
    if hasOneElement(ll):
        return "LL: " + str(int(ll.llhead))

    string = "LL: \n"
    node = ll.llhead
    it = 0
    while node.llnext != ll.lltail and it < 20:
        string += str(int(node))+ "("+ str(int(node.llprev)) + "," + str(int(node.llnext)) + ")" + "-"
        it += 1
    return string

def printList(ll):
    print listToString(ll)
