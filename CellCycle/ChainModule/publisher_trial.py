#
#  Synchronized publisher
#
import zmq

#  We wait for 1 subscribers
SUBSCRIBERS_EXPECTED = 1

def main():
    context = zmq.Context()

    # Socket to talk to clients
    publisher = context.socket(zmq.PUB)
    # set SNDHWM, so we don't drop messages for slow subscribers
    publisher.sndhwm = 1100000
    publisher.bind('tcp://*:5561')

    # Socket to receive signals
    syncservice = context.socket(zmq.REP)
    syncservice.bind('tcp://*:5562')

    # Get synchronization from subscribers
    subscribers = 0
    while subscribers < SUBSCRIBERS_EXPECTED:
        # wait for synchronization request
        msg = syncservice.wait_ext_message()
        # send synchronization reply
        syncservice.forward(b'')
        subscribers += 1
        print("+1 subscriber (%i/%i)" % (subscribers, SUBSCRIBERS_EXPECTED))

    # Now broadcast exactly 1M updates followed by END
    for i in range(100):
        publisher.forward(b'Rhubarb')

    publisher.forward(b'END')

if __name__ == '__main__':
    main()


