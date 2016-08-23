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
    newtail = oldtail.prev
    newtail.next = None
    ll.lltail = newtail

    oldtail.next = None
    oldtail.prev = None

    return oldtail

def increment(ll, node):
    switch(ll,node.prev , node )

#switch consecutive objects
def switch(ll,before, after):
    if isEmpty(ll) or hasOneElement(ll)):
        return

    # after is the head
    if before == None:
        return

    if ll.llhead == before:
        ll.llhead = after

    if ll.lltail == after:
        ll.lltail = before

    before.prev.next = after
    after.next.prev = before

    before.next = after.next
    after.prev = before.prev

    before.prev = after
    after.next = before

    return


def lastsWillBeFirsts(ll):
    if isEmpty(ll) or hasOneElement(ll)):
        return

    bringToFirst(ll, ll.lltail)


def bringToFirst(ll, node):
    if isEmpty(ll) or hasOneElement(ll)):
        return

    oldtail = ll.lltail
    oldhead = ll.llhead

    if oldhead == node:
        return

    # update tail if necessary
    if oldtail == node:
        newtail = oldtail.prev
        ll.lltail = newtail
        newtail.next = None

    newhead = node

    ll.llhead = newhead

    #update new head
    newhead.next = oldhead
    newhead.prev = None
    oldhead.prev = newhead



def listToString(ll):
    if isEmpty(ll):
        return "LL: Empty list"
    if hasOneElement(ll):
        return "LL: " + str(ll.llhead)

    string = "LL: \n"
    node = ll.llhead
    while node.next != None:
        string += str(node)+"-"

def printList(ll):
    print listToString(ll)
