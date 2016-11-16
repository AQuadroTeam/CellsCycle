#! /usr/bin/env python
from CellCycle.ChainModule.Message import InformationMessage
from ListCommunication import *
from Printer import *
from zmq import ZMQError
from ProdCons import ConsumerThread
from ChainFlow import *
from ListThread import Node
from cPickle import dumps, loads
from firstLaunchAWS import create_specific_instance_parameters
from DeadReader import DeadReader
from CycleStateMachine import TransitionTable
from ChainList import DeadList


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
        self.last_restore_message = ''
        self.last_restored_message = ''

        self.last_seen_random = '0'
        self.last_seen_priority = '0'
        self.last_seen_version = '0'

        self.restore_cycle_finished = False
        self.last_dead_node = None
        self.deads = DeadList()
        # self.first_time = True

        # TODO remove this and replace with canonicals check
        # if self.canonical_check():
        if self.myself.ip is '':
            # We are a new machine
            self.myself.ip = "127.0.0.1"
            # self.first_time = False
        # TODO remove this comment to deploy
        # else:
            # Let's begin with the memory part, this is the case of first boot

            # self.new_master_request()

        self.external_channel = ExternalChannel(addr=self.myself.ip, port=self.myself.ext_port, logger=self.logger)
        self.internal_channel = InternalChannel(addr=self.myself.ip, port=self.myself.int_port, logger=self.logger)

        self.node_to_add = ''

        # Prepare to add transition table

        transition_table_param = {"Free": [None, "pas", "pal", "pdl", "pds"],
                                  "BusyAddPS": ["added_or_pa", "paa_and_ps", "paa_and_pl", "pad_and_pl", "pad_and_ps"],
                                  "BusyAddPL": ["added_or_pa", "paa_and_ps", "paa_and_pl", "pad_and_pl", "pad_and_ps"],
                                  "BusyDeadPL": ["restored_or_pa", None, None, "pad_and_pl", "pad_and_ps"],
                                  "BusyDeadPS": ["restored_or_pa", None, None, "pad_and_pl", "pad_and_ps"]}

        states_param = ["Free", "BusyAddPS", "BusyAddPL", "BusyDeadPL", "BusyDeadPS"]

        self.transition_table = TransitionTable(states_param, transition_table_param, 0, self)

    def run(self):
        self.logger.debug(starting_writer(self.myself.id))
        self.writer_behavior()
        self.logger(exiting_writer(self.myself.id))

    def get_list(self):
        return self.node_list

    def logger_debug(self, msg):
        return self.logger.debug(msg)

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

    def clear_last_add_message(self):
        self.last_add_message = ''

    def clear_last_dead_message(self):
        self.last_dead_message = ''

    def clear_last_added_message(self):
        self.last_added_message = ''

    def clear_last_restored_message(self):
        self.last_restored_message = ''

    def get_last_add_message(self):
        return self.last_add_message

    def get_last_added_message(self):
        return self.last_added_message

    def get_last_dead_message(self):
        return self.last_dead_message

    def get_last_restored_message(self):
        return self.last_restored_message

    def update_last_seen(self, msg, source=EXT):
        if source == EXT:
            self.last_seen_version = msg.version
        self.last_seen_priority = msg.priority
        self.last_seen_random = msg.random

    def new_master_request(self):
        internal_channel_on_the_fly = InternalChannel(addr="127.0.0.1", port=self.myself.memory_port,
                                                      logger=self.logger)
        internal_channel_on_the_fly.generate_internal_channel_client_side()
        internal_channel_on_the_fly.send_first_internal_channel_message("NEED RESTORED")
        internal_channel_on_the_fly.wait_int_message(dont_wait=False)
        internal_channel_on_the_fly.close()

        # TODO remove above, this is the right code
        # master_of_master_to_send = self.node_list.get_value(self.master_of_master.id).master
        # memory_object = MemoryObject(master_of_master_to_send, self.master_of_master, self.master,
        # self.myself, self.slave)
        # loads(newMasterRequest("tcp://localhost:" + str(self.settings.getMasterSetPort()), memory_object))

    def new_slave_request(self):
        pass
        # slave_of_slave_to_send = self.node_list.get_value(self.slave_of_slave.id).slave
        # memory_object = MemoryObject(self.master, self.myself, self.slave,
        # self.slave_of_slave, slave_of_slave_to_send)
        # newSlaveRequest("tcp://localhost:" + str(self.settings.getMasterSetPort()), memory_object)

    def consider_add_message(self, msg, origin_message):
        relatives_check = self.is_one_of_my_relatives(msg.source_id)
        r_of_r_check = self.is_one_of_my_r_of_r(msg.source_id)
        # The ADD cycle isn't over or i'm not interested in adding new nodes
        someone_beats_me = not self.transition_table.get_current_state().can_scale_up()

        if relatives_check:
            if someone_beats_me:
                self.transition_table.change_state("paa_and_ps")
                self.logger.debug("i've just asked for scale up, but this node beats me : {}".
                                  format(msg.source_id))
            else:
                self.transition_table.change_state("pas")
        elif r_of_r_check:
            if someone_beats_me:
                self.transition_table.change_state("paa_and_pl")
                self.logger.debug("i've just asked for scale up, but this node beats me : {}".
                                  format(msg.source_id))
            else:
                self.transition_table.change_state("pal")
        else:
            #   if test == "r":
            #     self.transition_table.change_state("added_or_pa")
            self.logger.debug("none of my relatives : {}".
                              format(msg.source_id))

        self.update_and_forward_message(msg, origin_message)
        self.logger.debug("forwarding ADD message\n{}".format(msg.printable_message()))

    def consider_restored_message(self, msg, origin_message):
        dead_to_check = self.deads.get_value(msg.target_id)

        relatives_check = dead_to_check == "master" or dead_to_check == "slave" or \
            dead_to_check == "slave_of_slave" or dead_to_check == "master_of_master"

        r_of_r_check = dead_to_check == "mmm" or dead_to_check == "mmmm" or \
            dead_to_check == "sss" or dead_to_check == "ssss"

        if relatives_check or r_of_r_check:
            self.transition_table.change_state("restored_or_pa")

        self.deads.remove_from_list(msg.target_id)
        self.forward_message(origin_message)
        self.logger.debug("forwarding this RESTORED message\n{}".format(msg.printable_message()))

    def consider_restore_message(self, msg, origin_message):
        dead_to_check = self.deads.get_value(msg.target_id)

        relatives_check = dead_to_check == "master" or dead_to_check == "slave" or \
            dead_to_check == "slave_of_slave" or dead_to_check == "master_of_master"

        r_of_r_check = dead_to_check == "mmm" or dead_to_check == "mmmm" or \
            dead_to_check == "sss" or dead_to_check == "ssss"

        someone_beats_me = not self.transition_table.get_current_state().can_scale_up()

        if relatives_check:
            if someone_beats_me:
                self.transition_table.change_state("pad_and_ps")
                self.logger.debug("i've just asked for restore, but this node beats me : {}".
                                  format(msg.source_id))
            else:
                self.transition_table.change_state("pds")
        elif r_of_r_check:
            if someone_beats_me:
                self.transition_table.change_state("pad_and_pl")
                self.logger.debug("i've just asked for restore, but this node beats me : {}".
                                  format(msg.source_id))
            else:
                self.transition_table.change_state("pdl")
        else:
            # if test == "r":
            #     self.transition_table.change_state("restored_or_pa")
            self.logger.debug("none of my relatives : {}".
                              format(msg.source_id))

        self.update_and_forward_message(msg, origin_message)
        self.logger.debug("forwarding RESTORE message\n{}".format(msg.printable_message()))

    def consider_dead_message(self, msg, origin_message):
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
        mmm_result = self.node_list.get_value(self.master_of_master.id).master
        mmmm_result = self.node_list.get_value(mmm_result.id).master
        sss_result = self.node_list.get_value(self.slave_of_slave.id).slave
        ssss_result = self.node_list.get_value(sss_result.id).slave

        if msg.target_id == self.master.id:
            self.deads.add_in_list(msg.target_id, "master")
            self.master = self.master_of_master
            self.master_of_master = self.node_list.get_value(self.master_of_master.id).master
        elif msg.target_id == self.slave_of_slave.id:
            self.deads.add_in_list(msg.target_id, "slave_of_slave")
            self.slave_of_slave = self.node_list.get_value(msg.target_id).slave
        elif msg.target_id == self.master_of_master.id:
            self.deads.add_in_list(msg.target_id, "master_of_master")
            self.master_of_master = self.node_list.get_value(msg.target_id).master
        elif msg.target_id == mmm_result.id:
            self.deads.add_in_list(msg.target_id, "mmm")
        elif msg.target_id == mmmm_result.id:
            self.deads.add_in_list(msg.target_id, "mmmm")
        elif msg.target_id == sss_result.id:
            self.deads.add_in_list(msg.target_id, "sss")
        elif msg.target_id == ssss_result.id:
            self.deads.add_in_list(msg.target_id, "ssss")
        else:
            self.deads.add_in_list(msg.target_id, "None")

        can_scale_up = self.transition_table.get_current_state().can_scale_up()
        if self.is_one_of_my_relatives(msg.target_id) and can_scale_up:
            self.transition_table.change_state("pas")
        if self.is_one_of_my_r_of_r(msg.target_id) and can_scale_up:
            self.transition_table.change_state("pal")

        self.remove_from_list(msg.target_id)
        self.update_and_forward_message(msg, origin_message)
        self.logger.debug("forwarding this DEAD message\n{}".format(msg.printable_message()))

    def consider_added_message(self, msg, origin_message):
        self.logger.debug("my version is {}, uuu we have a new NODE\n{}".
                          format(str(self.version), msg.printable_message()))
        min_max_key = Node.to_min_max_key_obj(msg.target_key)
        # TODO remove this to deploy
        # node_to_add = Node(msg.target_id, msg.target_addr, self.settings.getIntPort(),
        #                    self.settings.getExtPort(),
        #                    min_max_key.min_key, min_max_key.max_key)
        added_int_port = "558{}".format(msg.target_id) if msg.target_id in ["1", "2", "3", "4", "5"] else "5586"
        added_ext_port = "559{}".format(msg.target_id) if msg.target_id in ["1", "2", "3", "4", "5"] else "5596"

        node_to_add = Node(msg.target_id, msg.target_addr, added_int_port,
                           added_ext_port,
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
        r_of_r_check = self.is_one_of_my_r_of_r(msg.source_id)

        if relatives_check or r_of_r_check:
            self.transition_table.change_state("added_or_pa")
            # this was the old version self.change_parents(node_to_add)
            self.change_parents()
            self.logger.debug("welcome new relative! now i am able to receive new scale ups, relatives:\n"
                              "{}, {}, {}, {}, {}".format(self.master_of_master.id, self.master.id, self.myself.id,
                                                          self.slave.id, self.slave_of_slave.id))

        self.forward_message(origin_message)
        self.logger.debug("forwarding this ADDED message\n{}".format(msg.printable_message()))

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
        self.logger.debug("this is my list\n{}".format(self.node_list.print_list()))

        tempt = 0
        while True:

            if tempt < 1:
                self.logger.debug(send_i_am_alive(self.myself.id, self.slave.id))
                tempt += 1

            self.forward_message(dumps(self.make_alive_node_msg(
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

    def forward_message(self, origin_message):
        try:
            self.external_channel.forward(origin_message)
        except zmq.Again as a:
            self.logger_debug("my slave is DEAD " + a.message)
            dead_message = self.make_dead_node_msg(target_id=self.master.id, target_addr=self.master.ip,
                                                   target_key=self.master.get_min_max_key(),
                                                   target_master_id=self.master_of_master.id)
            # if self.first_time:
            #     self.first_time = False
            # else:
            self.version = int(self.last_seen_version) + 1
            # generate a new channel to the slave_of_slave
            self.internal_channel.resync(msg=self.master_of_master.id)

            msg_to_send = to_external_message(self.version, dead_message)
            string_message = dumps(msg_to_send)
            self.external_channel.forward(string_message)
            self.last_dead_message = msg_to_send

            self.last_dead_node = self.slave
            self.remove_from_list(self.slave.id)

            # Change slave and slave of slave
            self.slave = self.slave_of_slave
            self.slave_of_slave = self.node_list.get_value(self.slave_of_slave.id).slave

            # Now update the list
            self.update_list(self.myself.id, self.master.id, self.slave.id)
            # Update the master node, the new master of target_slave is target_master
            self.change_master_to(target_node=self.slave.id, target_master=self.myself.id)
            # Update the slave node, the new slave of target_master is target_slave
            self.change_slave_to(target_node=self.myself.id, target_slave=self.slave.id)

            can_scale_up = self.transition_table.get_current_state().can_scale_up()
            if can_scale_up:
                self.transition_table.change_state("pds")
            else:
                self.transition_table.change_state("pad_and_ps")

    def update_and_forward_message(self, msg, origin_message, source=EXT):
        self.update_last_seen(msg, source)
        self.version = int(self.last_seen_version) + 1
        self.forward_message(origin_message)

    def consider_message(self, msg, origin_message):
        if is_dead_message(msg):
            self.consider_dead_message(msg, origin_message)
        if is_restore_message(msg):
            self.consider_restore_message(msg, origin_message)
        elif is_add_message(msg):
            self.consider_add_message(msg, origin_message)
        elif is_added_message(msg):
            self.consider_added_message(msg, origin_message)
        elif is_restored_message(msg):
            self.consider_restored_message(msg, origin_message)

    def analyze_message(self, msg):
        # Message from another process or a new node
        msg = loads(msg)

        if is_int_message(msg):
            # Now we have a simple object to handle with
            # if msg == "FINISHED" and self.dead_cycle_finished:
            if is_alive_message(msg):
                can_scale_up = self.transition_table.get_current_state().can_scale_up()
                if can_scale_up and msg.target_id == self.node_to_add:
                    self.internal_channel.reply_to_int_message(NOK)
                elif msg.target_id == self.slave_of_slave.id:
                    self.logger.debug("slave {} is DEAD, and why i don't realized it?".format(self.slave.id))
                    # Perhaps our slave is died
                    self.internal_channel.reply_to_int_message(NOK)
                else:
                    # In the future we can add an error code instead of empty msgs
                    self.internal_channel.reply_to_int_message(DIE)
            if is_scale_up_message(msg):
                can_scale_up = self.transition_table.get_current_state().can_scale_up()
                if can_scale_up:
                    self.internal_channel.reply_to_int_message(OK)
                    # if self.first_time:
                    #     self.first_time = False
                    # else:
                    self.version = int(self.last_seen_version) + 1
                    msg = self.make_add_node_msg(target_id=str(compute_son_id(float(self.myself.id),
                                                                              float(self.slave.id))),
                                                 target_key="0:19",
                                                 source_flag=INT, target_slave_id=self.slave.id)
                    msg_to_send = to_external_message(self.version, msg)
                    self.last_add_message = msg_to_send
                    self.transition_table.change_state("pas")
                    self.logger.debug("now i'm busy : ScaleUpThread asked to scale up")
                    string_message = dumps(msg_to_send)
                    self.update_and_forward_message(msg=msg_to_send, origin_message=string_message, source=INT)
                else:
                    # I'm busy, retry later if you want to add a new node
                    self.internal_channel.reply_to_int_message(NOK)
            if is_memory_request_finished_message(msg):
                self.internal_channel.reply_to_int_message(OK)
                internal_channel_on_the_fly = InternalChannel(addr=self.master.ip, port=self.master.int_port,
                                                              logger=self.logger)
                internal_channel_on_the_fly.generate_internal_channel_client_side()
                self.notify_restored(internal_channel_on_the_fly)
                internal_channel_on_the_fly.close()
            if is_memory_request_started_message(msg):
                # Start memory module process
                self.new_master_request()
            if is_restored_message(msg) and self.restore_cycle_finished:
                self.restore_cycle_finished = False
                self.internal_channel.reply_to_int_message(OK)
                min_max_key = Node.get_min_max_key(self.last_dead_node)
                msg = self.make_restored_node_msg(target_id=self.last_dead_node.id, target_key=min_max_key,
                                                  target_addr=self.last_dead_node.ip, source_flag=EXT,
                                                  target_master_id=self.master.id)
                self.version = int(self.last_seen_version) + 1
                msg = to_external_message(self.version, msg)
                self.last_restored_message = msg
                self.forward_message(dumps(msg))
            if is_added_message(msg):
                can_scale_up = self.transition_table.get_current_state().can_scale_up()
                if can_scale_up:
                    self.internal_channel.reply_to_int_message(NOK)
                else:
                    self.internal_channel.reply_to_int_message(dumps(self.node_list))
                    self.version = int(self.last_seen_version) + 1
                    msg_to_send = to_external_message(self.version, msg)
                    self.last_added_message = msg_to_send
                    string_message = dumps(msg_to_send)
                    # we send a notice to the next node
                    self.forward_message(string_message)
                    # and now we add the new node
                    min_max_key = Node.to_min_max_key_obj(msg.target_key)
                    added_int_port = "558{}".format(msg.target_id) if msg.target_id in \
                        ["1", "2", "3", "4", "5"] else "5586"
                    added_ext_port = "559{}".format(msg.target_id) if msg.target_id in \
                        ["1", "2", "3", "4", "5"] else "5596"

                    node_to_add = Node(msg.target_id, msg.target_addr, added_int_port,
                                       added_ext_port,
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
                    self.change_parents()

            if is_scale_down_message(msg):
                if self.transition_table.get_current_state().can_scale_down():
                    exit(0)
                # TODO replace with terminate instance and check for reply
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
                new_node_id_to_add = str(compute_son_id(float(self.myself.id), float(self.slave.id)))
                # new_node_keys_to_add = compute_son_key()
                new_node_instance_to_add = Node(new_node_id_to_add, "172.31.20.6", '5586',
                                                '5596',
                                                '0', '19')
                specific_parameters = [self.master, self.myself, new_node_instance_to_add, self.slave,
                                       self.slave_of_slave]

                self.last_add_message = ''
                self.node_to_add = msg.target_id
                # startInstanceAWS(self.settings, self.logger, create_specific_instance_parameters(specific_parameters))
                self.new_slave_request()
                # TODO generate node with startInstanceAWS
                create_single_process(l=self.logger, s=self.settings,
                                      a=create_specific_instance_parameters(specific_parameters))
                self.logger.debug("ADD CYCLE completed")
            elif is_my_last_added_message(msg, self.last_added_message):
                # The cycle is over
                self.last_added_message = ''
                # Now i'm free
                self.transition_table.change_state("added_or_pa")
                self.logger.debug("the cycle is over, now i am able to accept scale up requests")
                self.logger.debug("ADDED CYCLE completed, this is my list\n{}".format(self.node_list.print_list()))
            elif is_my_last_dead_message(msg, self.last_dead_message):
                # The cycle is over
                restore_message = self.make_restore_node_msg(target_id=msg.target_id,
                                                             target_addr=msg.target_addr,
                                                             target_key=msg.target_key,
                                                             target_master_id=msg.target_master_id)

                msg_to_send = to_external_message(self.version, restore_message)

                self.last_restore_message = msg_to_send
                self.last_dead_message = ''
                self.logger.debug("DEAD CYCLE completed")

                string_message = dumps(msg_to_send)
                if self.transition_table.get_current_state().can_restore():
                    self.update_and_forward_message(msg_to_send, string_message, source=INT)
                    if not self.transition_table.get_current_state().can_scale_up():
                        self.transition_table.change_state("pad_and_ps")
                    else:
                        self.transition_table.change_state("pas")

            elif is_my_last_restore_message(msg, self.last_restore_message):
                # The cycle is over
                self.last_restore_message = ''
                self.logger.debug("RESTORE CYCLE completed")
                self.restore_cycle_finished = True
                # Notify to the memory module
                self.new_slave_request()
                # Allow the slave to perform the memory request
                internal_channel_on_the_fly = InternalChannel(addr=self.slave.ip, port=self.slave.int_port,
                                                              logger=self.logger)
                internal_channel_on_the_fly.generate_internal_channel_client_side()
                self.notify_memory_request_started(internal_channel_on_the_fly)
                internal_channel_on_the_fly.close()
            elif is_my_last_restored_message(msg, self.last_restored_message):
                # The cycle is over
                self.last_dead_node = None
                self.transition_table.change_state("restored_or_pa")
                self.last_restored_message = ''
                self.logger.debug("RESTORED CYCLE completed, now i am able to receive scale up requests, "
                                  "this is my list\n{}".format(self.node_list.print_list()))
            else:
                if is_neutral_message(msg):
                    if int(msg.version) >= int(self.last_seen_version):
                        self.consider_message(msg, origin_message)
                else:
                    # if msg_variable_version_check(msg, self.last_seen_version):
                    #     self.consider_message(msg, origin_message, test="v")
                    if int(msg.version) >= int(self.last_seen_version):
                        if int(self.last_seen_priority) < int(msg.priority):
                            self.logger.debug("this message from {} can be forwarded"
                                              " due to higher priority than {}\n{}".
                                              format(msg.source_id, self.last_seen_priority, msg.printable_message()))
                            self.consider_message(msg, origin_message)
                        elif int(self.last_seen_priority) > int(msg.priority):
                            self.logger.debug("this message from {} can't be forwarded "
                                              "due to lower priority than {}\n{}".
                                              format(msg.source_id, self.last_seen_priority, msg.printable_message()))
                        elif int(self.last_seen_priority) == int(msg.priority):
                            if int(self.last_seen_random) < int(msg.random):
                                self.logger.debug("this message from {} can be forwarded "
                                                  "due to higher random than {}\n{}".
                                                  format(msg.source_id, self.last_seen_random, msg.printable_message()))
                                self.consider_message(msg, origin_message)
                            else:
                                self.logger.debug("this message from {} can't be forwarded"
                                                  " due to lower random than {}\n{}".
                                                  format(msg.source_id, self.last_seen_random, msg.printable_message()))
                    else:
                        self.logger.debug("this message will never be forwarded due to lower "
                                          "last seen version:\n"+msg.printable_message())


LOCAL_HOST = '127.0.0.1'
MYSELF = 'myself'
MASTER = 'master'
SLAVE = 'slave'
MASTER_OF_MASTER = 'master_of_master'
SLAVE_OF_SLAVE = 'slave_of_slave'

ID = 'id'
IP = 'ip'
MIN_KEY = 'min_key'
MAX_KEY = 'max_key'


class Generator:
    def __init__(self, logger, settings, json_arg):
        self.logger = logger
        self.settings = settings
        self.args = json_arg

    def _get_node_from_data(self, data):
        # return Node(data[ID], data[IP], self.settings.getIntPort(),
        #             self.settings.getExtPort(), min_key=data[MIN_KEY], max_key=data[MAX_KEY])

        if data[IP] == "172.31.20.6":

            int_port = "5586"
            ext_port = "5596"
            memory_port = "5576"
            return Node(data[ID], '', int_port,
                        ext_port, min_key=data[MIN_KEY], max_key=data[MAX_KEY], memory_port=memory_port)
        else:
            # int_port = "558{}".format(len("172.31.20."))
            # ext_port = "559{}".format(len("172.31.20."))
            int_port = "558{}".format(data[ID])
            ext_port = "559{}".format(data[ID])
            memory_port = "557{}".format(data[ID])
            return Node(data[ID], data[IP], int_port,
                        ext_port, min_key=data[MIN_KEY], max_key=data[MAX_KEY], memory_port=memory_port)

    def create_process_environment(self):
        myself = self.args[MYSELF]
        myself = self._get_node_from_data(myself)
        master = self.args[MASTER]
        master = self._get_node_from_data(master)
        slave = self.args[SLAVE]
        slave = self._get_node_from_data(slave)
        master_of_master = self.args[MASTER_OF_MASTER]
        master_of_master = self._get_node_from_data(master_of_master)
        slave_of_slave = self.args[SLAVE_OF_SLAVE]
        slave_of_slave = self._get_node_from_data(slave_of_slave)

        thread_reader_name = "Reader-{}".format(myself.id)
        thread_writer_name = "Writer-{}".format(myself.id)

        writer = DeadWriter(myself, master, slave, slave_of_slave, master_of_master, self.logger, self.settings,
                            thread_writer_name)
        reader = DeadReader(myself, master, slave, slave_of_slave, master_of_master, self.logger, self.settings,
                            thread_reader_name, writer)

        reader.start()
        writer.start()

        time.sleep(5)
        if myself.id not in ["1", "2", "3", "4", "5"]:
            from threading import Thread
            new_scale_up_thread = Thread(name="NewInstanceThread", target=new_instance_thread, args=(myself,
                                                                                                     self.logger,))
            new_scale_up_thread.start()

        reader.join()
    # unused
    # def create_process(self):
    #     Process(name='ListCommunicationProcess', target=Generator._create_process_environment(self))


def new_instance_thread(a, l):
    internal_channel = InternalChannel(addr='127.0.0.1', port=a.memory_port, logger=l)
    internal_channel.generate_internal_channel_client_side()
    time.sleep(2)
    internal_channel.send_first_internal_channel_message(message="FINISHED")
    internal_channel.wait_int_message(dont_wait=False)


def gen(l, s, a):
    generator = Generator(logger=l, settings=s, json_arg=a)
    generator.create_process_environment()


def create_single_process(l, s, a):
    l.debug("CREATING NEW PROCESS")
    from multiprocessing import Process
    new_process = Process(name="Process-NewBorn", target=gen, args=(l, s, a, ))
    new_process.start()
