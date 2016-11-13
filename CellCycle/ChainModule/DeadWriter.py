#! /usr/bin/env python
from CellCycle.AWS.AWSlib import startInstanceAWS, terminateThisInstanceAWS
from CellCycle.ChainModule.MemoryObject import MemoryObject
from CellCycle.ChainModule.Message import InformationMessage
from CellCycle.KeyCalcManager import keyCalcToCreateANewNode
from CellCycle.MemoryModule.MemoryManagement import newMasterRequest, newSlaveRequest
from CellCycle.MemoryModule.calculateSon import calculateSonId
from ListCommunication import *
from Printer import *
from zmq import ZMQError
from ProdCons import ConsumerThread
from ChainFlow import *
from ListThread import Node
from cPickle import dumps, loads
from firstLaunchAWS import create_specific_instance_parameters


class DeadWriter (ConsumerThread):

    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name):
        ConsumerThread.__init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name)
        self.logger.debug(these_are_my_features_writer(self.myself.id, self.master.id, self.slave.id,
                                                       self.myself.int_port,
                                                       self.myself.ext_port, self.myself.ip))
        # The version is handled by the dead writer
        self.version = 0

        self.last_add_message = ''
        self.last_added_message = ''
        self.last_dead_message = ''
        self.last_restored_message = ''

        self.last_seen_random = '0'
        self.last_seen_priority = '0'
        self.last_seen_version = '0'

        self.dead_cycle_finished = False
        self.last_dead_node = None

        self.external_channel = ExternalChannel(addr=self.myself.ip, port=self.myself.ext_port, logger=self.logger)
        self.internal_channel = InternalChannel(addr=self.myself.ip, port=self.myself.int_port, logger=self.logger)

        self.node_to_add = ''

    def run(self):
        self.logger.debug(starting_writer(self.myself.id))
        self.writer_behavior()
        self.logger(exiting_writer(self.myself.id))

    def set_list(self, new_list):
        self.node_list = new_list

    def set_version(self, new_version):
        self.version = new_version

    def set_last_seen_version(self, new_last_seen_version):
        self.last_seen_version = new_last_seen_version

    def set_last_seen_priority(self, new_last_seen_priority):
        self.last_seen_priority = new_last_seen_priority

    def set_last_seen_random(self, new_last_seen_random):
        self.last_seen_random = new_last_seen_random

    def update_last_seen(self, msg):
        self.last_seen_version = msg.version
        self.last_seen_priority = msg.priority
        self.last_seen_random = msg.random

    def new_master_request(self):
        # internal_channel_on_the_fly = InternalChannel(addr="127.0.0.1", port=self.myself.memory_port,
        #                                               logger=self.logger)
        # internal_channel_on_the_fly.generate_internal_channel_client_side()
        # internal_channel_on_the_fly.send_first_internal_channel_message("NEED RESTORED")
        # internal_channel_on_the_fly.wait_int_message(dont_wait=False)

        # remove above, this is the right code
        master_of_master_to_send = self.node_list.get_value(self.master_of_master.id).master
        memory_object = MemoryObject(master_of_master_to_send, self.master_of_master, self.master,
                                     self.myself, self.slave)
        newMasterRequest("tcp://localhost:" + str(self.settings.getMasterSetPort()), memory_object)

    def first_boot_new_master_request(self):
        # internal_channel_on_the_fly = InternalChannel(addr="127.0.0.1", port=self.myself.memory_port,
        #                                               logger=self.logger)
        # internal_channel_on_the_fly.generate_internal_channel_client_side()
        # internal_channel_on_the_fly.send_first_internal_channel_message("NEED RESTORED")
        # internal_channel_on_the_fly.wait_int_message(dont_wait=False)

        # remove above, this is the right code
        master_of_master_to_send = self.master_of_master
        memory_object = MemoryObject(master_of_master_to_send, self.master, self.myself,
                                     self.slave, self.slave_of_slave)
        newMasterRequest("tcp://localhost:" + str(self.settings.getMasterSetPort()), memory_object)
        self.internal_channel.wait_int_message(dont_wait=False)
        
        self.logger.debug("memory module finished, let's start writer behavior")

    def new_slave_request(self):
        slave_of_slave_to_send = self.node_list.get_value(self.slave_of_slave.id).slave
        memory_object = MemoryObject(self.master, self.myself, self.slave,
                                     self.slave_of_slave, slave_of_slave_to_send)
        newSlaveRequest("tcp://localhost:" + str(self.settings.getMasterSetPort()), memory_object)

    def consider_add_message(self, msg, origin_message):
        relatives_check = self.is_one_of_my_relatives(msg.source_id)
        # The ADD cycle isn't over or i'm not interested in adding new nodes
        someone_beats_me = self.last_add_message != '' and self.node_to_add == ''
        if someone_beats_me:
            self.busy_add = False
            self.logger.debug("i've just asked for scale up, but this node beats me : {}".
                              format(msg.source_id))
        if relatives_check and not self.busy_add:
            self.busy_add = True
            self.update_last_seen(msg)
            self.version = max(int(msg.version) + 1, self.version)
            self.external_channel.forward(origin_message)
            self.logger.debug("is relative and not busy, new version {} and MSG\n{}".
                              format(str(self.version), msg.printable_message()))
        elif not relatives_check:
            # self.busy_add = True
            self.update_last_seen(msg)
            self.version = max(int(msg.version) + 1, self.version)
            self.external_channel.forward(origin_message)
            self.logger.debug("not one of relatives, new version {} and MSG\n{}".
                              format(str(self.version), msg.printable_message()))
        else:
            self.logger.debug("my version is still {}, no forward and MSG\n{}".
                              format(str(self.version), msg.printable_message()))

    def consider_restored_message(self, msg, origin_message):
        relatives_check = self.is_one_of_my_relatives(msg.source_id)
        if relatives_check:
            self.busy_add = False
        self.update_last_seen(msg)
        self.version = max(int(msg.version) + 1, self.version)
        self.external_channel.forward(origin_message)
        self.logger.debug("forwarding this RESTORED message\n{}".format(msg.printable_message()))

    def consider_dead_message(self, msg, origin_message):
        # TODO check that this is the right order to update the list
        self.change_dead_keys_to(msg.source_id)
        target_id = msg.target_id
        target_master = msg.target_relative_id
        target_slave = msg.source_id

        # Update the target ID
        self.update_list(target_node=target_id, target_master=target_master, target_slave=target_slave)
        # Update the master node, the new master of target_slave is target_master
        self.change_master_to(target_node=target_slave, target_master=target_master)
        # Update the slave node, the new slave of target_master is target_slave
        self.change_slave_to(target_node=target_master, target_slave=target_slave)

        # if this node is one of my relatives, let's update our static attributes
        if msg.target_id == self.slave.id:
            self.slave = self.slave_of_slave
            self.slave_of_slave = self.node_list.get_value(self.slave_of_slave.id).slave
            # Let's resync with our new slave
            self.logger.debug("resync with {}".format(self.slave.id))

            # notify the memory module, no response necessary
            self.new_slave_request()
            # internal_channel_on_the_fly = InternalChannel(addr="localhost",
            # port=settings.getMemoryObjectPort(),
            # logger=logger)
            # internal_channel_on_the_fly.generate_internal_channel_server_side()
            # internal_channel_on_the_fly.wait_int_message(dont_wait=False)
            # internal_channel_on_the_fly.reply_to_int_message(OK)
            # resync sending the new master of master
            self.internal_channel.resync(msg=dumps(self.master))
        if msg.target_id == self.slave_of_slave.id:
            self.slave_of_slave = self.node_list.get_value(msg.target_id).slave
        # No case of master.addr
        if msg.target_id == self.master_of_master.id:
            self.master_of_master = self.node_list.get_value(msg.target_id).master
        if self.is_one_of_my_relatives(msg.target_id):
            self.busy_add = True
            self.logger.debug("now i'm busy : {} is DEAD".format(msg.target_id))
            # if i'm involved i have to be busy
        self.remove_from_list(msg.target_id)
        self.change_parents_from_list()
        self.update_last_seen(msg)
        self.version = max(int(msg.version) + 1, self.version)
        self.external_channel.forward(origin_message)
        self.logger.debug("forwarding this DEAD message\n{}".format(msg.printable_message()))

    def consider_added_message(self, msg, origin_message):
        self.logger.debug("my version is {}, uuu we have a new NODE\n{}".
                          format(str(self.version), msg.printable_message()))

        # new_memory_obj = self.get_memory_obj_from_new_node(msg)

        # before creating adding the new node to the list let's update the old keys
        self.change_added_keys_to(msg.source_id)

        min_max_key = Node.to_min_max_key_obj(msg.target_key)
        node_to_add = Node(msg.target_id, msg.target_addr, self.settings.getIntPort(),
                           self.settings.getExtPort(),
                           min_max_key.min_key, min_max_key.max_key)
        self.logger.debug("adding in list this node\n{}".format(node_to_add.print_values()))

        target_master = self.node_list.get_value(msg.source_id).target
        target_slave = self.node_list.get_value(msg.target_relative_id).target
        # Add the new node in list
        self.add_in_list(target_node=node_to_add, target_master=target_master,
                         target_slave=target_slave)

        target_id = msg.target_id
        target_master = msg.source_id
        target_slave = msg.target_relative_id

        # Update the master node, the new master of target_slave is target_id
        self.change_master_to(target_node=target_slave, target_master=target_id)
        # Update the slave node, the new master of target_master is target_id
        self.change_slave_to(target_node=target_master, target_slave=target_id)

        self.logger.debug("this is my new list\n{}".format(self.node_list.print_list()))

        relatives_check = self.is_one_of_my_relatives(msg.source_id)
        if relatives_check:
            self.busy_add = False
            self.change_parents_from_list()
            # if new_memory_obj is not None:
            #     self.distribute_my_own_added_keys(new_memory_obj, node_to_add)
            self.logger.debug("welcome new relative! now i am able to receive new scale ups")

        self.update_last_seen(msg)
        self.version = max(int(msg.version) + 1, self.version)
        self.external_channel.forward(origin_message)

    def writer_behavior(self):

        self.internal_channel.generate_internal_channel_server_side()

        if self.canonical_check():
            # Let's begin with the memory part, this is the case of first boot
            self.first_boot_new_master_request()

        loads(self.internal_channel.wait_int_message(dont_wait=False))

        self.internal_channel.reply_to_int_message(msg=OK)

        # Now build publisher socket

        self.external_channel.generate_external_channel_server_side()
        self.external_channel.external_channel_publish()

        # Why do we need this sleep???
        time.sleep(1)
        # Just a check for dead nodes
        # if self.myself.id == '1':
        #    time.sleep(100000000000000000)
        self.logger.debug("this is my list\n{}".format(self.node_list.print_list()))

        tempt = 0
        while True:

            if tempt < 1:
                self.logger.debug(send_i_am_alive(self.myself.id, self.slave.id))
                tempt += 1

            self.external_channel.forward(dumps(self.make_alive_node_msg(
                self.myself.id, self.master.id, source_flag=EXT)))

            try:
                req_rep_msg = self.internal_channel.wait_int_message(dont_wait=True)
                # This is the part where we handle an int message
                # Now we have a simple object to handle with
                self.analyze_message(req_rep_msg)
            except ZMQError:
                # self.logger.debug(nothing_to_receive())
                pass

            item = self.consume()

            if item is not None:
                # self.logger.debug(this_is_my_item(self.myself.id, item))
                self.analyze_message(item)

            # Sleep for WRITER_TIMEOUT (1 millisecond)
            time.sleep(WRITER_TIMEOUT)

    def wait_the_new_node_and_send_the_list(self):

        msg = loads(self.internal_channel.wait_int_message(dont_wait=False))

        while not(is_int_message(msg) and is_alive_message(msg) and msg.target_id == self.node_to_add):
            self.internal_channel.reply_to_int_message(NOK)
            msg = loads(self.internal_channel.wait_int_message(dont_wait=False))
        # It's the right node
        information_message = InformationMessage(node_list=self.node_list, version=self.version,
                                                 last_seen_version=self.last_seen_version,
                                                 last_seen_priority=self.last_seen_priority,
                                                 last_seen_random=self.last_seen_random)

        self.internal_channel.reply_to_int_message(dumps(information_message))

    def analyze_message(self, msg):
        # Message from another process or a new node
        msg = loads(msg)

        if is_int_message(msg):
            # Now we have a simple object to handle with
            if is_alive_message(msg):
                if self.busy_add and msg.target_id == self.node_to_add:
                    self.internal_channel.reply_to_int_message(NOK)
                elif msg.target_id == self.slave_of_slave.id:
                    self.logger.debug("slave {} is DEAD, waiting for DEAD message".format(self.slave.id))
                    # Perhaps our slave is died
                    self.internal_channel.reply_to_int_message(NOK)
                else:
                    # In the future we can add an error code instead of empty msgs
                    self.internal_channel.reply_to_int_message(DIE)
            if is_add_message(msg):
                if not self.busy_add:
                    self.internal_channel.reply_to_int_message(OK)
                    # self.version += 1
                    memory_obj = MemoryObject(self.master_of_master, self.master, self.myself,
                                              self.slave, self.slave_of_slave)
                    new_min_max_key = keyCalcToCreateANewNode(memory_obj).newNode
                    min_max_key_string = "{}:{}".format(str(new_min_max_key.min_key), str(new_min_max_key.max_key))
                    msg = self.make_add_node_msg(target_id=str(calculateSonId(float(self.myself.id),
                                                                              float(self.slave.id))),
                                                 target_key=min_max_key_string,
                                                 source_flag=INT, target_slave_id=self.slave.id)
                    msg_to_send = to_external_message(self.version, msg)
                    self.last_add_message = msg_to_send
                    self.busy_add = True
                    self.logger.debug("now i'm busy : ScaleUpThread asked to scale up")
                    string_message = dumps(msg_to_send)
                    self.external_channel.forward(string_message)
                else:
                    # I'm busy, retry later if you want to add a new node
                    self.internal_channel.reply_to_int_message(NOK)
            if is_restored_message(msg) and self.dead_cycle_finished:
                self.dead_cycle_finished = False
                self.internal_channel.reply_to_int_message(OK)
                min_max_key = Node.get_min_max_key(self.last_dead_node)
                msg = self.make_restored_node_msg(target_id=self.last_dead_node.id, target_key=min_max_key,
                                                  target_addr=self.last_dead_node.ip, source_flag=EXT,
                                                  target_master_id=self.master.id)
                self.version += 1
                msg = to_external_message(self.version, msg)
                self.last_restored_message = msg
                self.external_channel.forward(dumps(msg))
                '''
                if not self.busy_add:
                    self.internal_channel.reply_to_int_message(NOK)
                else:
                    self.internal_channel.reply_to_int_message(OK)
                    self.version += 1
                    msg_to_send = to_external_message(self.version, msg)
                    self.last_restored_message = msg_to_send
                    string_message = dumps(msg_to_send)
                    self.external_channel.forward(string_message)
                '''
            if is_added_message(msg):
                if not self.busy_add:
                    self.internal_channel.reply_to_int_message(NOK)
                else:
                    self.internal_channel.reply_to_int_message(dumps(self.node_list))
                    self.version += 1
                    msg_to_send = to_external_message(self.version, msg)
                    self.last_added_message = msg_to_send
                    string_message = dumps(msg_to_send)
                    # we send a notice to the next node
                    self.external_channel.forward(string_message)
            if is_dead_message(msg):
                # if i am the target just DIE
                if msg.target_id == self.myself.id:
                    terminateThisInstanceAWS(settings=self.settings, logger=self.logger)

                # self.version += 1
                msg_to_send = to_external_message(self.version, msg)
                string_message = dumps(msg_to_send)
                self.external_channel.forward(string_message)
                self.last_dead_message = msg_to_send
                # The check for the already self.busy_add == True is missing
                self.busy_add = True
                self.logger.debug("now i'm busy : my master is DEAD")

                self.last_dead_node = self.master
                self.remove_from_list(self.master.id)

                # Change master and master of master
                self.master = self.master_of_master
                self.master_of_master = self.node_list.get_value(self.master_of_master.id).master

                # Now update the list
                self.update_list(self.myself.id, self.master.id, self.slave.id)

        else:
            # self.logger.debug(just_received_new_msg(self.myself.id, self.master.id,
            #                                         msg.printable_message()))
            # Save the origin message just to avoid another conversion, remember
            # that we send strings
            origin_message = dumps(msg)
            # Now we have a simple object to handle with
            # msg = msg

            # This is an external message, let's check if it's none of my business
            if is_my_last_add_message(msg, self.last_add_message):
                self.logger.debug("LAST ADD message")
                # The cycle is over
                # We have to wait for a new node
                memory_obj = MemoryObject(self.master_of_master, self.master, self.myself,
                                          self.slave, self.slave_of_slave)
                new_min_max_key = keyCalcToCreateANewNode(memory_obj).newNode

                new_node_id_to_add = str(calculateSonId(float(self.myself.id), float(self.slave.id)))
                new_node_instance_to_add = Node(new_node_id_to_add, None, self.settings.getIntPort(),
                                                self.settings.getExtPort(),
                                                new_min_max_key.min_key, new_min_max_key.max_key)
                specific_parameters = [self.master, self.myself, new_node_instance_to_add, self.slave,
                                       self.slave_of_slave]

                self.last_add_message = ''
                self.node_to_add = msg.target_id
                startInstanceAWS(self.settings, self.logger, create_specific_instance_parameters(specific_parameters))
                self.new_slave_request()
                self.logger.debug("ADD CYCLE completed")
            elif is_my_last_added_message(msg, self.last_added_message):
                # The cycle is over
                self.last_added_message = ''
                self.busy_add = False
                self.logger.debug("the cycle is over, now i am able to accept scale up requests")

                # new_memory_obj = self.get_memory_obj_from_new_node(msg)

                # before creating adding the new node to the list let's update the old keys
                self.change_added_keys_to(msg.source_id)

                # now we can add the new node
                min_max_key = Node.to_min_max_key_obj(msg.target_key)

                node_to_add = Node(msg.target_id, msg.target_addr, self.settings.getIntPort(),
                                   self.settings.getExtPort(),
                                   min_max_key.min_key, min_max_key.max_key)
                self.logger.debug("adding this node in list\n{}".format(node_to_add.print_values()))

                target_master = self.node_list.get_value(msg.source_id).target
                target_slave = self.node_list.get_value(msg.target_relative_id).target
                # Add the new node in list
                self.add_in_list(target_node=node_to_add, target_master=target_master,
                                 target_slave=target_slave)

                target_id = msg.target_id
                target_master = msg.source_id
                target_slave = msg.target_relative_id

                # Update the master node, the new master of target_slave is target_id
                self.change_master_to(target_node=target_slave, target_master=target_id)
                # Update the slave node, the new master of target_master is target_id
                self.change_slave_to(target_node=target_master, target_slave=target_id)

                self.wait_the_new_node_and_send_the_list()
                self.change_parents_from_list()
                # if new_memory_obj is not None:
                #     self.distribute_my_own_added_keys(new_memory_obj, node_to_add)
                self.node_to_add = ''
                self.logger.debug("ADDED CYCLE completed, this is my list\n{}".format(self.node_list.print_list()))
            elif is_my_last_dead_message(msg, self.last_dead_message):
                # The cycle is over
                self.last_dead_message = ''
                self.logger.debug("DEAD CYCLE completed")
                # Notify to the memory module
                self.new_master_request()
                self.dead_cycle_finished = True
            elif is_my_last_restored_message(msg, self.last_restored_message):
                # The cycle is over
                self.last_restored_message = ''
                self.busy_add = False
                self.logger.debug("RESTORED CYCLE completed, now i am able to receive scale up requests, "
                                  "this is my list\n{}".format(self.node_list.print_list()))
            else:
                if msg_variable_version_check(msg, self.version):

                    # Check if the node is DEAD
                    if is_dead_message(msg):
                        self.change_dead_keys_to(msg.source_id)
                        target_id = msg.target_id
                        target_master = msg.target_relative_id
                        target_slave = msg.source_id

                        # Update the target ID
                        self.update_list(target_node=target_id, target_master=target_master, target_slave=target_slave)
                        # Update the master node, the new master of target_slave is target_master
                        self.change_master_to(target_node=target_slave, target_master=target_master)
                        # Update the slave node, the new slave of target_master is target_slave
                        self.change_slave_to(target_node=target_master, target_slave=target_slave)

                        # if this node is one of my relatives, let's update our static attributes
                        if msg.target_id == self.slave.id:
                            self.slave = self.slave_of_slave
                            self.slave_of_slave = self.node_list.get_value(self.slave_of_slave.id).slave
                            # Let's resync with our new slave
                            self.logger.debug("resync with {}".format(self.slave.id))

                            # TODO notify the memory module, no response necessary
                            self.new_slave_request()
                            # internal_channel_on_the_fly = InternalChannel(addr="localhost",
                            # port=settings.getMemoryObjectPort(),
                            # logger=logger
                            # internal_channel_on_the_fly.generate_internal_channel_server_side()
                            # internal_channel_on_the_fly.wait_int_message(dont_wait=False)
                            # internal_channel_on_the_fly.reply_to_int_message(OK)
                            # resync sending the new master of master
                            self.internal_channel.resync(msg=dumps(self.master))
                        if msg.target_id == self.slave_of_slave.id:
                            self.slave_of_slave = self.node_list.get_value(msg.target_id).slave
                        # No case of master.addr
                        if msg.target_id == self.master_of_master.id:
                            self.master_of_master = self.node_list.get_value(msg.target_id).master
                        if self.is_one_of_my_relatives(msg.target_id):
                            self.busy_add = True
                            self.logger.debug("now i'm busy : {} is DEAD".format(msg.target_id))
                            # if i'm involved i have to be busy
                        self.remove_from_list(msg.target_id)
                        self.change_parents_from_list()
                        self.update_last_seen(msg)
                        self.version = max(int(msg.version) + 1, self.version)
                        self.external_channel.forward(origin_message)
                        self.logger.debug("forwarding this DEAD message\n{}".format(msg.printable_message()))
                    elif is_add_message(msg):
                        check_to_consider_add_message = (self.last_add_message != '' and
                                                         version_random_priority_check(msg, self.last_add_message))\
                                                        or self.last_add_message == ''
                        if check_to_consider_add_message:
                            relatives_check = self.is_one_of_my_relatives(msg.source_id)
                            # The ADD cycle isn't over or i'm not interested in adding new nodes
                            someone_beats_me = self.last_add_message != '' and self.node_to_add == ''
                            if someone_beats_me:
                                self.busy_add = False
                                self.logger.debug("i've just asked for scale up, but this node beats me : {}".
                                                  format(msg.source_id))
                            if relatives_check and not self.busy_add:
                                self.busy_add = True
                                self.update_last_seen(msg)
                                self.version = max(int(msg.version) + 1, self.version)
                                self.external_channel.forward(origin_message)
                                self.logger.debug("is relative and not busy, new version {} and MSG\n{}".
                                                  format(str(self.version), msg.printable_message()))
                            elif not relatives_check:
                                # self.busy_add = True
                                self.update_last_seen(msg)
                                self.version = max(int(msg.version) + 1, self.version)
                                self.external_channel.forward(origin_message)
                                self.logger.debug("not one of relatives, new version {} and MSG\n{}".
                                                  format(str(self.version), msg.printable_message()))
                            else:
                                self.logger.debug("my version is still {}, no forward and MSG\n{}".
                                                  format(str(self.version), msg.printable_message()))
                    elif is_added_message(msg):
                        check_to_consider_added_message = (self.last_added_message != '' and
                                                           version_random_priority_check(msg, self.last_added_message))\
                                                          or self.last_added_message == ''
                        if check_to_consider_added_message:
                            self.logger.debug("my version is {}, uuu we have a new NODE\n{}".
                                              format(str(self.version), msg.printable_message()))

                            # new_memory_obj = self.get_memory_obj_from_new_node(msg)

                            # before creating adding the new node to the list let's update the old keys
                            self.change_added_keys_to(msg.source_id)

                            min_max_key = Node.to_min_max_key_obj(msg.target_key)
                            node_to_add = Node(msg.target_id, msg.target_addr, self.settings.getIntPort(),
                                               self.settings.getExtPort(),
                                               min_max_key.min_key, min_max_key.max_key)

                            self.logger.debug("adding this node in list\n{}".format(node_to_add.print_values()))

                            target_master = self.node_list.get_value(msg.source_id).target
                            target_slave = self.node_list.get_value(msg.target_relative_id).target
                            # Add the new node in list
                            self.add_in_list(target_node=node_to_add, target_master=target_master,
                                             target_slave=target_slave)

                            target_id = msg.target_id
                            target_master = msg.source_id
                            target_slave = msg.target_relative_id

                            # Update the master node, the new master of target_slave is target_id
                            self.change_master_to(target_node=target_slave, target_master=target_id)
                            # Update the slave node, the new master of target_master is target_id
                            self.change_slave_to(target_node=target_master, target_slave=target_id)

                            self.logger.debug("this is my new list\n{}".format(self.node_list.print_list()))

                            relatives_check = self.is_one_of_my_relatives(msg.source_id)
                            if relatives_check:
                                self.busy_add = False
                                self.change_parents_from_list()
                                # if new_memory_obj is not None:
                                # self.distribute_my_own_added_keys(new_memory_obj, node_to_add)
                                self.logger.debug("welcome new relative! now i am able to receive new scale ups")

                            self.update_last_seen(msg)
                            self.version = max(int(msg.version) + 1, self.version)
                            self.external_channel.forward(origin_message)
                    elif is_restored_message(msg):
                        relatives_check = self.is_one_of_my_relatives(msg.source_id)
                        if relatives_check:
                            self.busy_add = False
                        self.update_last_seen(msg)
                        self.version = max(int(msg.version) + 1, self.version)
                        self.external_channel.forward(origin_message)
                        self.logger.debug("forwarding this RESTORED message\n{}".format(msg.printable_message()))

                    # Let's begin our selfish control, but first we want to have a rest just to have a small delay
                    # This control is necessary to understand if our messages were kicked out from the list cycle
                    time.sleep(1)
                    if self.last_dead_message != '' and version_random_priority_check(msg, self.last_dead_message):
                        self.update_last_seen(msg)
                        self.version = max(int(msg.version) + 1, self.version)
                        self.last_dead_message.version = self.version
                        string_message = dumps(self.last_dead_message)
                        self.external_channel.forward(string_message)

                    if self.last_add_message != '':
                        if version_random_priority_check(msg, self.last_add_message):
                            if self.busy_add:
                                # This is the case in which someone won with a higher message
                                self.last_add_message = ''
                            else:
                                self.update_last_seen(msg)
                                self.version = max(int(msg.version) + 1, self.version)
                                self.last_add_message.version = self.version
                                string_message = dumps(self.last_add_message)
                                self.logger.debug("this message MUST be resent \n" +
                                                  self.last_add_message.printable_message() + " because i RECEIVED \n" +
                                                  msg.printable_message())
                                self.external_channel.forward(string_message)
                        else:
                            self.logger.debug("this message will never be forwarded, i have a major random"
                                              " :\n"+msg.printable_message())

                    if self.last_added_message != '' and version_random_priority_check(msg, self.last_added_message):
                        self.update_last_seen(msg)
                        self.version = max(int(msg.version) + 1, self.version)
                        self.last_added_message.version = self.version
                        string_message = dumps(self.last_added_message)
                        self.external_channel.forward(string_message)

                    if self.last_restored_message != '' and \
                            version_random_priority_check(msg, self.last_restored_message):
                        self.update_last_seen(msg)
                        self.version = max(int(msg.version) + 1, self.version)
                        self.last_restored_message.version = self.version
                        string_message = dumps(self.last_restored_message)
                        self.external_channel.forward(string_message)
                elif int(msg.version) == int(self.last_seen_version):
                    if int(self.last_seen_priority) < int(msg.priority):
                        self.last_seen_random = msg.random
                        self.logger.debug("this message from {} can be forwarded due to higher priority than {}\n{}".
                                          format(msg.source_id, self.last_seen_priority, msg.printable_message()))
                        self.last_seen_priority = msg.priority
                        # self.external_channel.forward(dumps(msg))
                        if is_added_message(msg):
                            self.consider_added_message(msg, dumps(msg))
                        # elif is_add_message(msg):
                        #     self.consider_add_message(msg, dumps(msg))
                        elif is_dead_message(msg):
                            self.consider_dead_message(msg, dumps(msg))
                        # elif is_restored_message(msg):
                        #     self.consider_restored_message(msg, dumps(msg))
                        else:
                            self.external_channel.forward(dumps(msg))
                    elif int(self.last_seen_priority) > int(msg.priority):
                        self.logger.debug("this message from {} can't be forwarded due to lower priority than {}\n{}".
                                          format(msg.source_id, self.last_seen_priority, msg.printable_message()))
                    elif int(self.last_seen_priority) == int(msg.priority):
                        if int(self.last_seen_random) < int(msg.random):
                            self.logger.debug("this message from {} can be forwarded due to higher random than {}\n{}".
                                              format(msg.source_id, self.last_seen_random, msg.printable_message()))
                            self.last_seen_random = msg.random
                            # self.external_channel.forward(dumps(msg))
                            if is_added_message(msg):
                                self.consider_added_message(msg, dumps(msg))
                            # elif is_add_message(msg):
                            #     self.consider_add_message(msg, dumps(msg))
                            elif is_dead_message(msg):
                                self.consider_dead_message(msg, dumps(msg))
                            else:
                                self.external_channel.forward(dumps(msg))
                            # elif is_restored_message(msg):
                            #     self.consider_restored_message(msg, dumps(msg))
                        else:
                            self.logger.debug("this message from {} can't be forwarded due to lower random than {}\n{}".
                                              format(msg.source_id, self.last_seen_random, msg.printable_message()))
                else:
                    self.logger.debug("this message will never be forwarded :\n"+msg.printable_message())

