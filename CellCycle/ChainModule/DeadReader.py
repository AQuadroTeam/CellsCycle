#! /usr/bin/env python

from ProdCons import ProducerThread
from ListCommunication import *
from zmq import Again
from Printer import *
from ChainFlow import *
from ListThread import Node
from cPickle import loads, dumps


class DeadReader(ProducerThread):
    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings):
        ProducerThread.__init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings)
        self.logger.debug(these_are_my_features_reader(self.myself.id, self.master.id, self.slave.id))
        # We know nothing, no dead_message, no version. We only check if our master replies

        self.external_channel = ExternalChannel(addr=self.master.ip, port=self.master.ext_port, logger=self.logger)
        self.internal_channel = InternalChannel(addr=self.master.ip, port=self.master.int_port, logger=self.logger)
        self.last_dead_node = ''

    def run(self):
        self.logger.debug(starting_reader(self.myself.id))
        self.wait_for_a_dead()
        self.logger.debug(exiting_reader(self.myself.id))

    # Why is this function here ???
    # def set_proper_timeout(self, nodes=DEF_NODES, special_lap=False):
    #    if special_lap:
    #        index_timeout = int(self.myself) - 1
    #        change_timeout = index_timeout % nodes
    #        node_timeout = (change_timeout + 1)*nodes
        # else:

    # Let's begin the connection between us and our next node
    def init_connection(self):
        self.internal_channel.generate_internal_channel_client_side()
        self.internal_channel.send_first_internal_channel_message(
            dumps(self.make_alive_node_msg(source_flag=INT, target_id=self.myself.id, target_master_id=self.master.id)))

        self.internal_channel.wait_int_message(dont_wait=False)

        self.external_channel.generate_external_channel_client_side()
        self.external_channel.external_channel_subscribe()

    def is_dead_message_and_i_am_the_slave(self, message):
        return message.target_id == self.last_dead_node

    '''
    Why is this function here???
    def renewConnection(self):
        # Too much hardcoded
        listCommunication = ListCommunication(DEFAULT_ADDR,'5186')
        listCommunication.init_client_socket()
        self.logger.debug('Writer ' + self.myself + ' waiting for sync with node '
         + self.slaveId + ' with address ' + listCommunication.complete_address)
        listCommunication.start_client_connection()
        self.logger.debug('Sync completed. New client socket (Writer ' + self.myself + ') to node '
         + self.slaveId + ' with address ' + listCommunication.complete_address)
        return listCommunication
    '''

    def change_master(self):
        self.master = self.master_of_master
        self.master_of_master = None

    def change_master_of_master(self, new_master_of_master):
        self.master_of_master = new_master_of_master

    def wait_for_a_dead(self):

        self.init_connection()

        while True:

            try:
                message = self.external_channel.wait_ext_message()

                origin_message = message
                message = loads(message)

                if is_alive_message(message):
                    if is_dead_and_i_am_the_target(message, self.myself.id):
                        self.logger.debug(i_am_dead_goodbye(self.myself))
                        self.external_channel.close()
                        exit(1)

                    if is_added_message(message):
                        if self.is_my_new_master(message):
                            # This is the part when i connect to another publisher
                            self.external_channel.close()

                            min_max_key = Node.to_min_max_key_obj(message.target_key)
                            self.master_of_master = self.master
                            self.master = Node(node_id=message.target_id, ip=message.target_addr,
                                               min_key=min_max_key.min_key, max_key=min_max_key.max_key,
                                               int_port=self.settings.getIntPort(), ext_port=self.settings.getExtPort())
                            self.init_connection()
                            # list_communication = self.init_connection()
                        self.logger.debug(new_node_added(message.target_id))
                    if self.is_dead_message_and_i_am_the_slave(message):
                        self.last_dead_node = ''
                        self.internal_channel.send_int_message()
                        self.internal_channel.send_internal_message_client_side(
                            self.make_alive_node_msg(source_flag=INT, target_id=self.myself.id,
                                                     target_master_id=self.master.id))
                        new_master_of_master = self.internal_channel.wait_int_message(dont_wait=False)
                        new_master_of_master = loads(new_master_of_master)
                        min_max_key = Node.to_min_max_key_obj(new_master_of_master.target_key)
                        new_master_of_master = Node(new_master_of_master.target_id, new_master_of_master.target_addr,
                                                    ext_port=self.settings.getExtPort(),
                                                    int_port=self.settings.getIntPort(),
                                                    max_key=min_max_key.max_key, min_key=min_max_key.min_key)

                        self.change_master_of_master(new_master_of_master=new_master_of_master)

                    '''
                    This is a special case, for now we don't consider it
                    if not is_in_list(message,self.node_list):
                        if message[2] == PRIORITY_DEAD:
                            self.logger.debug('Hey you are not in the list!')
                        else:
                            self.logger.
                            debug('Hey ' + message[11] + ' you are not in the list! You are supposed to be dead!')
                    '''

                self.produce(origin_message)

                self.logger.debug(just_received_new_msg(self.myself.id, self.master.id, origin_message))

            except Again:

                dead_message = self.make_dead_node_msg(target_id=self.master.id, target_addr=self.master.ip,
                                                       target_key=self.master.get_min_max_key(),
                                                       target_master_id=self.master_of_master.id)
                self.last_dead_node = self.master.id
                '''
                This is a special case, for now we don't consider it
                if not (self.masterId in self.node_list):
                    self.logger.debug('Probably i missed something')
                    exit(1)
                else:
                '''

                self.produce(dead_message)
                self.logger.debug(this_is_my_dead_message(self.myself.id, self.master.id, dead_message))
                self.last_dead_node = self.master.id

                self.change_master()

                # This is the part when i connect to another publisher
                self.external_channel.close()

                # just subscribe to another publisher for now
                self.external_channel.generate_external_channel_client_side()
                self.external_channel.external_channel_subscribe(self.master.ip, self.master.ext_port)
