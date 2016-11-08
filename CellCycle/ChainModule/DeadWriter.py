#! /usr/bin/env python

from ListCommunication import *
from Printer import *
from zmq import ZMQError
from ProdCons import ConsumerThread
from ChainFlow import *
from ListThread import Node
from cPickle import dumps, loads


class DeadWriter (ConsumerThread):

    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name):
        ConsumerThread.__init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name)
        self.logger.debug(these_are_my_features_writer(self.myself.id, self.master.id, self.slave.id))
        # The version is handled by the dead writer
        self.version = 0

        self.last_add_message = ''
        self.last_added_message = ''
        self.last_dead_message = ''
        self.last_restored_message = ''

        self.external_channel = ExternalChannel(addr=self.myself.ip, port=self.myself.ext_port, logger=self.logger)
        self.internal_channel = InternalChannel(addr=self.myself.ip, port=self.myself.int_port, logger=self.logger)

    def run(self):
        self.logger.debug(starting_writer(self.myself.id))
        self.writer_behavior()
        self.logger(exiting_writer(self.myself.id))

    def writer_behavior(self):

        self.internal_channel.generate_internal_channel_server_side()

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

    def analyze_message(self, msg):
        # Message from another process or a new node
        msg = loads(msg)

        if is_int_message(msg):
            # Now we have a simple object to handle with
            if is_alive_message(msg):
                if self.busy_add:
                    self.internal_channel.reply_to_int_message(dumps(self.node_list))
                elif msg.target_id == self.slave_of_slave.id:
                    # Perhaps our slave is died
                    self.internal_channel.reply_to_int_message(NOK)
                else:
                    # In the future we can add an error code instead of empty msgs
                    self.internal_channel.reply_to_int_message(DIE)
            if is_add_message(msg):
                if not self.busy_add:
                    self.internal_channel.reply_to_int_message(OK)
                    self.version += 1
                    msg_to_send = to_external_message(self.version, msg)
                    self.last_add_message = msg_to_send
                    self.busy_add = True
                    string_message = dumps(msg_to_send)
                    self.external_channel.forward(string_message)
                else:
                    # I'm busy, retry later if you want to add a new node
                    self.internal_channel.reply_to_int_message(NOK)
            if is_restored_message(msg):
                if not self.busy_add:
                    self.internal_channel.reply_to_int_message(NOK)
                else:
                    self.internal_channel.reply_to_int_message(OK)
                    self.version += 1
                    msg_to_send = dumps(self.version, msg)
                    self.last_restored_message = msg_to_send
                    string_message = dumps(msg_to_send)
                    self.external_channel.forward(string_message)
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
                    # sync with the new node addr
                    self.internal_channel.resync()
            if is_dead_message(msg):
                # if i am the target just DIE
                if msg.target_id == self.myself.id:
                    exit(0)
                self.version += 1
                msg_to_send = to_external_message(self.version, msg)
                string_message = dumps(msg_to_send)
                self.external_channel.forward(string_message)
                self.last_dead_message = msg_to_send
                # The check for the already self.busy_add == True is missing
                self.busy_add = True
                self.remove_from_list(self.master.id)

                # Change master and master of master
                self.master = self.master_of_master
                self.master_of_master = self.node_list.get_value(self.master_of_master.id).master

                # Now update the list
                self.update_list(self.myself.id, self.master.id, self.slave.id)

                # notify memory process about the new node
                self.internal_channel.notify_dead_node(settings=self.settings, message=self.master_of_master)

        else:
            # Save the origin message just to avoid another conversion, remember
            # that we send strings
            origin_message = dumps(msg)
            # Now we have a simple object to handle with
            # msg = msg

            # This is an external message, let's check if it's none of my business
            if is_my_last_add_message(msg, self.last_add_message):
                # The cycle is over
                # We have to wait for a new node
                # Now invoke Amazon's API
                self.last_add_message = ''
            elif is_my_last_added_message(msg, self.last_added_message):
                # The cycle is over
                self.last_added_message = ''
                self.busy_add = False
                self.internal_channel.reply_to_int_message(dumps(self.node_list))
            elif is_my_last_dead_message(msg, self.last_dead_message):
                # The cycle is over
                self.last_dead_message = ''
                self.logger.debug("DEAD CYCLE completed")
                # TODO restored message
            elif is_my_last_restored_message(msg, self.last_restored_message):
                # The cycle is over
                self.last_restored_message = ''
                self.busy_add = False
            else:
                if msg_variable_version_check(msg, self.version):

                    if self.last_dead_message != '' and version_random_priority_check(msg, self.last_dead_message):
                        self.version += 1
                        string_message = dumps(self.last_dead_message)
                        self.external_channel.forward(string_message)

                    if self.last_add_message != '' and version_random_priority_check(msg, self.last_add_message):
                        self.version += 1
                        string_message = dumps(self.last_add_message)
                        self.external_channel.forward(string_message)

                    if self.last_added_message != '' and version_random_priority_check(msg, self.last_added_message):
                        self.version += 1
                        string_message = dumps(self.last_added_message)
                        self.external_channel.forward(string_message)

                    if self.last_restored_message != '' and \
                            version_random_priority_check(msg, self.last_restored_message):
                        self.version += 1
                        string_message = dumps(self.last_restored_message)
                        self.external_channel.forward(string_message)

                    # Check if the node is DEAD
                    if is_dead_message(msg):
                        target_id = msg.target_id
                        target_master = msg.target_relative_id
                        target_slave = msg.source_id

                        # Update the target ID
                        self.update_list(target_node=target_id, target_master=target_master, target_slave=target_slave)
                        # Update the master node, the new master of target_slave is target_master
                        self.change_master_to(target_node=target_slave, target_master=target_id)
                        # Update the slave node, the new slave of target_master is target_slave
                        self.change_slave_to(target_node=target_master, target_slave=target_id)

                        # if this node is one of my relatives, let's update our static attributes
                        if msg.target_id == self.slave.id:
                            self.slave = self.slave_of_slave
                            self.slave_of_slave = self.node_list.get_value(self.slave_of_slave.id).slave
                            # Send master of master ip
                            # min_max_key = self.master.get_min_max_key()
                            # Let's resync with our new slave
                            self.logger.debug("resync with {}".format(self.slave.id))
                            # elf.internal_channel.resync(
                            #     msg=dumps(self.make_added_node_msg(target_id=self.master.id,
                            #                                        target_key=min_max_key,
                            #                                        target_addr=self.master.ip,
                            #                                        target_slave_id=self.slave.id)))
                            # resync sending the new master of master
                            self.internal_channel.resync(msg=dumps(self.master))
                        if msg.target_id == self.slave_of_slave.id:
                            self.slave_of_slave = self.node_list.get_value(msg.target_id).slave
                        # No case of master.addr
                        if msg.target_id == self.master_of_master.id:
                            self.master_of_master = self.node_list.get_value(msg.target_id).master
                        if self.is_one_of_my_relatives(msg.target_id):
                            self.busy_add = True
                            # if i'm involved i have to be busy
                        self.remove_from_list(msg.target_id)
                        self.version += 1
                        self.external_channel.forward(origin_message)
                    elif is_add_message(msg):
                        relatives_check = self.is_one_of_my_relatives(msg.target_id)
                        if relatives_check and not self.busy_add:
                            self.busy_add = True
                            self.version += 1
                            self.external_channel.forward(origin_message)
                        elif not relatives_check:
                            self.version += 1
                            self.external_channel.forward(origin_message)
                    elif is_added_message(msg):
                        min_max_key = Node.to_min_max_key_obj(msg.target_key)
                        node_to_add = Node(msg.target_id, msg.target_addr, self.settings.getIntPort(),
                                           self.settings.getExtPort(),
                                           min_max_key.min_key, min_max_key.max_key)
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

                        relatives_check = self.is_one_of_my_relatives(msg.target_id)
                        if relatives_check:
                            self.busy_add = False
                        self.version += 1
                        self.external_channel.forward(origin_message)
                    elif is_restored_message(msg):
                        relatives_check = self.is_one_of_my_relatives(msg.target_id)
                        if relatives_check:
                            self.busy_add = False
                        self.version += 1
                        self.external_channel.forward(origin_message)
