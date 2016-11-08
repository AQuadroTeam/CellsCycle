#! /usr/bin/env python

from ProdCons import ProducerThread
from ListCommunication import *
from zmq import Again
from Printer import *
from ChainFlow import *
from ListThread import Node
from cPickle import loads, dumps


class DeadReader(ProducerThread):
    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name):
        ProducerThread.__init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name)
        self.logger.debug(these_are_my_features_reader(self.myself.id, self.master.id, self.slave.id))
        # We know nothing, no dead_message, no version. We only check if our master replies

        self.external_channel = ExternalChannel(addr=self.master.ip, port=self.master.ext_port, logger=self.logger)
        self.internal_channel = InternalChannel(addr=self.master.ip, port=self.master.int_port, logger=self.logger)

    def run(self):
        self.logger.debug(starting_reader(self.myself.id))
        self.wait_for_a_dead()
        self.logger.debug(exiting_reader(self.myself.id))

    # Let's begin the connection between us and our next node
    def init_connection(self):
        self.logger.debug("sync init")
        self.internal_channel.generate_internal_channel_client_side()

        stop = False
        while not stop:
            self.internal_channel.send_first_internal_channel_message(
                dumps(self.make_alive_node_msg(source_flag=INT, target_id=self.myself.id,
                                               target_master_id=self.master.id)))

            rep_msg = self.internal_channel.wait_int_message(dont_wait=False)
            if self.master_of_master is None:
                if not (rep_msg == NOK or rep_msg == DIE):
                    rep_msg = loads(rep_msg)
                    self.change_master_of_master(rep_msg)
                    stop = True
                else:
                    self.logger.debug("wrong information at sync time, retry in 0.5 seconds")
                    time.sleep(0.5)
            else:
                stop = True

        self.logger.debug("accepted by master {}".format(self.master.id))

        self.external_channel.generate_external_channel_client_side()
        self.external_channel.external_channel_subscribe()
        self.logger.debug("sync completed")

    def change_master(self):
        self.master = self.master_of_master
        self.master_of_master = None

    def change_master_of_master(self, new_master_of_master):
        self.master_of_master = new_master_of_master

    def wait_for_a_dead(self):
        while True:
            self.init_connection()

            tempt = 0
            stop = False

            while not stop:

                try:
                    message = self.external_channel.wait_ext_message()

                    origin_message = message
                    message = loads(message)

                    if not is_alive_message(message):
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
                                                   int_port=self.settings.getIntPort(),
                                                   ext_port=self.settings.getExtPort())
                                self.init_connection()
                            self.logger.debug(new_node_added(message.target_id))

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

                        if tempt < 1:
                            self.logger.debug(just_received_new_msg(self.myself.id, self.master.id,
                                                                    message.printable_message()))
                            tempt += 1

                except Again:

                    dead_message = self.make_dead_node_msg(target_id=self.master.id, target_addr=self.master.ip,
                                                           target_key=self.master.get_min_max_key(),
                                                           target_master_id=self.master_of_master.id)
                    '''
                    This is a special case, for now we don't consider it
                    if not (self.masterId in self.node_list):
                        self.logger.debug('Probably i missed something')
                        exit(1)
                    else:
                    '''

                    self.produce(dumps(dead_message))
                    if tempt < 1:
                        self.logger.debug(this_is_my_dead_message(self.myself.id, self.master.id,
                                                                  dead_message.printable_message()))
                        tempt += 1

                    self.change_master()

                    # This is the part when i connect to another publisher
                    self.external_channel.close()
                    self.internal_channel.close()

                    # renew channels

                    self.internal_channel = InternalChannel(addr=self.master.ip, port=self.master.int_port,
                                                            logger=self.logger)
                    self.external_channel = ExternalChannel(addr=self.master.ip, port=self.master.ext_port,
                                                            logger=self.logger)

                    stop = True
