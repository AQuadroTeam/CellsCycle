import zmq
import time
from zmq import Again
from Printer import *
from Const import TRIES, TRY_TIMEOUT, OK

BACKLOG = 5
MAX_BUFF = 1024
MAX_RCVTIMEO = 2000
DEFAULT_ADDR = 'tcp://localhost'


class ListCommunication:

    def __init__(self, addr="*", port="8080", logger=None):
        self.logger = logger
        # create a socket object
        self.context = zmq.Context()
        self.complete_address = Address(addr, port).complete_address
        self.sync_address = ''
        # Socket used with the following node
        self.list_communication_channel = None

        # This part is just for test
        # if port == '5555':
        #     self.sync_address = Address(addr, '5562').complete_address
        # elif port == '5556':
        #     self.sync_address = Address(addr, '5563').complete_address
        # elif port == '5557':
        #     self.sync_address = Address(addr, '5564').complete_address

    def open_sub_socket(self):
        self.list_communication_channel = self.context.socket(zmq.SUB)
        # This is necessary because a subscriber needs a timeout for updates
        self.set_rcv_timeo()

        # self.external_channel.RCVTIMEO = MAX_RCVTIMEO

    def open_pub_socket(self):
        self.list_communication_channel = self.context.socket(zmq.PUB)

    def open_rep_socket(self, sync_addr=None):
        # Socket to receive signals
        self.list_communication_channel = self.context.socket(zmq.REP)
        if sync_addr is not None:
            self.list_communication_channel.bind(sync_addr)
        else:
            self.list_communication_channel.bind(self.sync_address)

    def open_req_socket(self, sync_addr=None):
        # Second, synchronize with publisher
        self.list_communication_channel = self.context.socket(zmq.REQ)
        if sync_addr is not None:
            self.list_communication_channel.connect(sync_addr)
        else:
            self.list_communication_channel.connect(self.sync_address)

    def set_rcv_timeo(self, timeout=MAX_RCVTIMEO):
        self.list_communication_channel.RCVTIMEO = timeout

    def close(self):
        self.list_communication_channel.close()
        self.context.destroy()
        self.logger.debug(closing_socket_with(self.complete_address))
        # self.list_communication_channel.disconnect(self.completeAddress)

    # TODO notify_dead_node
    def notify_dead_node(self, address):
        pass

    @staticmethod
    def store_data(data, file_path):
        with open(file_path, 'w+') as f:
            f.write(data)
            f.close()

    def send_from_file(self, file_path):
        with open(file_path, 'r') as f:
            data = f.read()
            self.list_communication_channel.send(data)
            f.close()


class ExternalChannel(ListCommunication):

    def __init__(self, addr="*", port="8080", logger=None):
        ListCommunication.__init__(self, addr=addr, port=port, logger=logger)

    # This function initializes a new external channel server side with a publisher socket
    def generate_external_channel_server_side(self):
        self.logger.debug(generating_server_connection_point(self.complete_address))
        self.open_pub_socket()

    # After creating a pub socket we need to bind it to receive subscriptions
    def external_channel_publish(self):
        # bind to the port
        self.list_communication_channel.bind(self.complete_address)

    def reset(self):
        self.list_communication_channel.close()
        self.context.destroy()
        self.context = zmq.Context()
        # try without a restart because we can have an address already in use
        self.generate_external_channel_server_side()

    # This function initializes a new external channel client side with a subscriber socket
    def generate_external_channel_client_side(self):
        self.logger.debug(generating_client_connection_point(self.complete_address))
        self.open_sub_socket()

    def wait_ext_message(self):
        #  Wait for next request
        message = self.list_communication_channel.recv()
        return message

    # Forward a new external message like a router
    def forward(self, data):
        tries = 0
        while tries < TRIES:
            try:
                self.list_communication_channel.send(data)
            except Again:
                time.sleep(TRY_TIMEOUT)

    def external_channel_subscribe(self, addr=DEFAULT_ADDR, port=None):
        # connection to hostname on the port.
        # e.g. self.external_channel.connect("tcp://localhost:5555")
        if port is not None:
            self.complete_address = '{}:{}'.format(addr, port)
        self.list_communication_channel.connect(self.complete_address)
        self.list_communication_channel.setsockopt(zmq.SUBSCRIBE, b'')

        # #############################

        # Let the server take its time
        time.sleep(0.1)


class InternalChannel(ListCommunication):

    def __init__(self, addr="*", port="8080", logger=None):
        ListCommunication.__init__(self, addr=addr, port=port, logger=logger)

    # After generating an external channel we need an internal channel to receive internal messages
    def generate_internal_channel_server_side(self):
        # ###################
        self.open_rep_socket()

    # As a client we generate an internal channel first to notify our existence to the next node,
    # then to send other internal messages
    # The correct flow to synchronize should be : generate_internal_channel_client_side -> first_sync
    def generate_internal_channel_client_side(self, sync_addr=None):
        self.open_req_socket(sync_addr)

    def wait_int_message(self, dont_wait=True):
        if dont_wait:
            # wait for internal message
            try:
                msg = self.list_communication_channel.recv(zmq.DONTWAIT)
                return msg
            except Again:
                raise Again
        else:
            msg = self.list_communication_channel.recv()
            return msg

    def reply_to_int_message(self, msg='ACK'):
        self.send_int_message(msg=msg)

    def send_int_message(self, msg=b'ALIVE'):
        stop = False

        while not stop:
            try:
                self.list_communication_channel.send(msg)
                stop = True
            except Again:
                time.sleep(TRY_TIMEOUT)

    def send_internal_message_client_side(self, message):
        self.send_int_message(message)

    def send_internal_message_server_side(self, message):
        self.send_int_message(message)

    def resync(self, msg=OK):
        self.wait_int_message(dont_wait=False)

        self.reply_to_int_message(msg=msg)

    # Let's try with the first alive message, send it to the server
    def first_sync(self):

        # Send alive to the server
        self.send_int_message()

        # wait for synchronization reply
        self.list_communication_channel.recv()

        # self.external_channel.setsockopt(zmq.SUBSCRIBE, '')


class Address:

    def __init__(self, ip, port=''):
        self.ip = ip
        self.port = port
        self.complete_address = 'tcp://{}:{}'.format(self.ip, self.port)

'''
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send(b"World")
'''