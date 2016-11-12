#! /usr/bin/env python
from CellCycle.AWS.AWSlib import stopThisInstanceAWS
from CellCycle.ChainModule.MemoryObject import MemoryObject
from CellCycle.MemoryModule.MemoryManagement import newStartRequest
from ProdCons import ProducerThread
from ListCommunication import *
from zmq import Again
from Printer import *
from ChainFlow import *
from ListThread import Node
from cPickle import loads, dumps


class DeadReader(ProducerThread):
    """This is a reader thread that waits for its master.
    If TIMEOUT passes then the master is DEAD.

    """

    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name,
                 writer_instance):
        ProducerThread.__init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name)
        self.logger.debug(these_are_my_features_reader(self.myself.id, self.master.id, self.slave.id,
                                                       self.myself.int_port, self.myself.ext_port, self.myself.ip))
        # We know nothing, no dead_message, no version. We only check if our master replies

        self.external_channel = ExternalChannel(addr=self.master.ip, port=self.master.ext_port, logger=self.logger)
        self.internal_channel = InternalChannel(addr=self.master.ip, port=self.master.int_port, logger=self.logger)

        self.internal_channel_memory = InternalChannel(addr="localhost", port=self.settings.getMemoryObjectPort(),
                                                       logger=self.logger)

        self.writer_instance = writer_instance

    def run(self):
        self.logger.debug(starting_reader(self.myself.id))
        self.wait_for_a_dead()
        self.logger.debug(exiting_reader(self.myself.id))

    def new_start_request(self):
        memory_object = MemoryObject(self.master_of_master, self.master, self.myself, self.slave, self.slave_of_slave)
        newStartRequest("tcp://localhost:" + str(self.settings.getMasterSetPort()), memory_object)
        # wait for added by memory module
        self.internal_channel_memory.generate_internal_channel_server_side()
        self.internal_channel_memory.wait_int_message(dont_wait=False)
        self.internal_channel_memory.reply_to_int_message(OK)

    def retry_until_success(self, msg, times):
        stop = False
        while not stop:
            self.internal_channel.send_first_internal_channel_message(msg)

            rep_msg = self.internal_channel.wait_int_message(dont_wait=False)

            if not (rep_msg == NOK or rep_msg == DIE):
                rep_msg = loads(rep_msg)
                if times == 2:
                    self.node_list = rep_msg.node_list
                    self.writer_instance.set_list(self.node_list)
                    self.logger.debug("received the new list\n{}".format(self.node_list.print_list()))
                    self.writer_instance.set_version(rep_msg.version)
                    self.writer_instance.set_last_seen_version(rep_msg.last_seen_version)
                    self.writer_instance.set_last_seen_priority(rep_msg.last_seen_priority)
                    self.writer_instance.set_last_seen_random(rep_msg.last_seen_random)

                stop = True
            else:
                self.logger.debug("wrong information at sync time, retry in 0.5 seconds")
                time.sleep(0.5)

    def new_birth_connection(self):
        self.logger.debug("new birth sync init")

        self.new_start_request()

        self.internal_channel.generate_internal_channel_client_side()

        min_max_keys = Node.get_min_max_key(self.myself)
        new_added_node_message = self.make_added_node_msg(target_id=self.myself.id, target_slave_id=self.slave.id,
                                                          target_addr=self.myself.ip, target_key=min_max_keys,
                                                          source_flag=INT, source_id=self.master.id)
        self.retry_until_success(dumps(new_added_node_message), 1)

        new_alive_node_message = self.make_alive_node_msg(source_flag=INT, target_id=self.myself.id,
                                                          target_master_id=self.master.id)
        self.retry_until_success(dumps(new_alive_node_message), 2)

        self.logger.debug("new accepted by master {}".format(self.master.id))

        self.external_channel.generate_external_channel_client_side()
        self.external_channel.external_channel_subscribe()
        self.logger.debug("new birth sync completed")
        # newMasterRequest(Address(self.master.ip, self.settings.getMasterSetPort()).complete_address,
        # self.node_list.get_value(self.master.id))

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
        # newMasterRequest(Address(self.master.ip, self.settings.getMasterSetPort()).complete_address,
        # self.node_list.get_value(self.master.id))

    def change_master(self):
        self.master = self.master_of_master
        self.master_of_master = None

    def change_master_of_master(self, new_master_of_master):
        self.master_of_master = new_master_of_master

    def wait_for_a_dead(self):
        first_step = True
        while True:
            if not self.canonical_check() and first_step:
                self.new_birth_connection()
                first_step = False
            else:
                self.logger.debug("my IP is not none : {}".format(self.myself.ip))
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
                            stopThisInstanceAWS(settings=self.settings, logger=self.logger)

                        if is_added_message(message):
                            if self.is_my_new_master(message):
                                # This is the part when i connect to another publisher

                                min_max_key = Node.to_min_max_key_obj(message.target_key)
                                self.master_of_master = self.master
                                self.master = Node(node_id=message.target_id, ip=message.target_addr,
                                                   min_key=min_max_key.min_key, max_key=min_max_key.max_key,
                                                   int_port=self.settings.getIntPort(),
                                                   ext_port=self.settings.getExtPort())

                                self.logger.debug("added node as new master\n{}".format(self.master.print_values()))
                                self.external_channel.close()
                                self.internal_channel.close()
                                self.internal_channel = InternalChannel(addr=self.master.ip, port=self.master.int_port,
                                                                        logger=self.logger)
                                self.external_channel = ExternalChannel(addr=self.master.ip, port=self.master.ext_port,
                                                                        logger=self.logger)
                                stop = True
                            elif self.is_my_new_master_of_master(message):
                                # This is the part when i connect to another publisher

                                min_max_key = Node.to_min_max_key_obj(message.target_key)
                                self.master_of_master = Node(node_id=message.target_id, ip=message.target_addr,
                                                             min_key=min_max_key.min_key, max_key=min_max_key.max_key,
                                                             int_port=self.settings.getIntPort(),
                                                             ext_port=self.settings.getExtPort())

                                self.logger.debug("added node as new master_of_master\n{}".format(
                                    self.master.print_values()))
                                self.external_channel.close()
                                self.internal_channel.close()
                                self.internal_channel = InternalChannel(addr=self.master.ip, port=self.master.int_port,
                                                                        logger=self.logger)
                                self.external_channel = ExternalChannel(addr=self.master.ip, port=self.master.ext_port,
                                                                        logger=self.logger)
                                stop = True

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

                        # if tempt < 1:
                        # self.logger.debug(just_received_new_msg(self.myself.id, self.master.id,
                        #                                         message.printable_message()))
                        #     tempt += 1

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
                    # TODO wait restored message
                    # internal_channel_on_the_fly =
                    # InternalChannel(addr="localhost", port=settings.getMemoryObjectPort(),
                    #  logger=logger
                    # internal_channel_on_the_fly.generate_internal_channel_server_side()
                    # internal_channel_on_the_fly.wait_int_message(dont_wait=False)
                    # internal_channel_on_the_fly.reply_to_int_message(OK)
