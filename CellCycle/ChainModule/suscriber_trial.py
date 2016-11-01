#
#  Synchronized subscriber
#
import time

import zmq

def main():
    context = zmq.Context()

    # First, connect our subscriber socket
    subscriber = context.socket(zmq.SUB)
    subscriber.connect('tcp://localhost:5561')
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')

    time.sleep(1)

    # Second, synchronize with publisher
    syncclient = context.socket(zmq.REQ)
    syncclient.connect('tcp://localhost:5562')

    # send a synchronization request
    syncclient.forward(b'')

    # wait for synchronization reply
    syncclient.wait_ext_message()

    # Third, get our updates and report how many we got
    nbr = 0
    while True:
        msg = subscriber.wait_ext_message()
        if msg == b'END':
            break
        nbr += 1

    print ('Received %d updates' % nbr)

if __name__ == '__main__':
    main()

