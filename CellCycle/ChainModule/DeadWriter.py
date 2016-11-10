#! /usr/bin/env python

from ListCommunication import *
from Printer import *
from zmq import ZMQError
from ProdCons import ConsumerThread
from ChainFlow import *
from ListThread import Node
from cPickle import dumps, loads
from firstLaunchAWS import create_specific_instance_parameters
from DeadReader import DeadReader


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

        # TODO remove this
        if self.myself.ip is '':
            self.myself.ip = "127.0.0.1"
        self.external_channel = ExternalChannel(addr=self.myself.ip, port=self.myself.ext_port, logger=self.logger)
        self.internal_channel = InternalChannel(addr=self.myself.ip, port=self.myself.int_port, logger=self.logger)

        self.node_to_add = ''

    def run(self):
        self.logger.debug(starting_writer(self.myself.id))
        self.writer_behavior()
        self.logger(exiting_writer(self.myself.id))

    def update_last_seen(self, msg):
        self.last_seen_version = msg.version
        self.last_seen_priority = msg.priority
        self.last_seen_random = msg.random

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

    def wait_the_new_node_and_send_the_list(self):

        msg = loads(self.internal_channel.wait_int_message(dont_wait=False))

        while not(is_int_message(msg) and is_alive_message(msg) and msg.target_id == self.node_to_add):
            self.internal_channel.reply_to_int_message(NOK)
            msg = loads(self.internal_channel.wait_int_message(dont_wait=False))
        # It's the right node
        self.internal_channel.reply_to_int_message(dumps(self.node_list))

    def analyze_message(self, msg):
        # Message from another process or a new node
        msg = loads(msg)

        if is_int_message(msg):
            # Now we have a simple object to handle with
            if is_alive_message(msg):
                if self.busy_add and msg.target_id == self.node_to_add:
                    self.internal_channel.reply_to_int_message(NOK)
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
                    msg = self.make_add_node_msg(target_id=str(compute_son_id(float(self.myself.id),
                                                                              float(self.slave.id))),
                                                 target_key="0:19",
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
            if is_restored_message(msg):
                if not self.busy_add:
                    self.internal_channel.reply_to_int_message(NOK)
                else:
                    self.internal_channel.reply_to_int_message(OK)
                    self.version += 1
                    msg_to_send = to_external_message(self.version, msg)
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
                self.logger.debug("now i'm busy : my master is DEAD")

                self.remove_from_list(self.master.id)

                # Change master and master of master
                self.master = self.master_of_master
                self.master_of_master = self.node_list.get_value(self.master_of_master.id).master

                # Now update the list
                self.update_list(self.myself.id, self.master.id, self.slave.id)

                # notify memory process about the new node
                # TODO notify memory module
                self.internal_channel.notify_dead_node(settings=self.settings, message=self.master_of_master)

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

                # startInstanceAWS(self.settings, self.logger, create_specific_instance_parameters(specific_parameters))
                self.last_add_message = ''
                self.node_to_add = msg.target_id
                create_single_process(l=self.logger, s=self.settings,
                                      a=create_specific_instance_parameters(specific_parameters))
                self.logger.debug("ADD CYCLE completed")
                # TODO generate_node
            elif is_my_last_added_message(msg, self.last_added_message):
                # The cycle is over
                self.last_added_message = ''
                self.busy_add = False
                self.logger.debug("the cycle is over, now i am able to accept scale up requests")

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

                self.wait_the_new_node_and_send_the_list()
                self.node_to_add = ''
                self.change_parents(node_to_add)
                self.logger.debug("ADDED CYCLE completed, this is my list\n{}".format(self.node_list.print_list()))
            elif is_my_last_dead_message(msg, self.last_dead_message):
                # The cycle is over
                self.last_dead_message = ''
                self.logger.debug("DEAD CYCLE completed")
                # TODO restored message to test
            elif is_my_last_restored_message(msg, self.last_restored_message):
                # The cycle is over
                self.last_restored_message = ''
                self.busy_add = False
                self.logger.debug("the node is restored, now i am able to receive scale up requests")
            else:
                if msg_variable_version_check(msg, self.version):

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
                            # Let's resync with our new slave
                            self.logger.debug("resync with {}".format(self.slave.id))
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
                        self.update_last_seen(msg)
                        self.version = int(msg.version) + 1
                        self.external_channel.forward(origin_message)
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
                                self.version = int(msg.version) + 1
                                self.external_channel.forward(origin_message)
                                self.logger.debug("is relative and not busy, new version {} and MSG\n{}".
                                                  format(str(self.version), msg.printable_message()))
                            elif not relatives_check:
                                # self.busy_add = True
                                self.update_last_seen(msg)
                                self.version = int(msg.version) + 1
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

                            relatives_check = self.is_one_of_my_relatives(msg.source_id)
                            if relatives_check:
                                self.busy_add = False
                                self.change_parents(node_to_add)
                                self.logger.debug("welcome new relative! now i am able to receive new scale ups")

                            self.update_last_seen(msg)
                            self.version = int(msg.version) + 1
                            self.external_channel.forward(origin_message)
                    elif is_restored_message(msg):
                        relatives_check = self.is_one_of_my_relatives(msg.source_id)
                        if relatives_check:
                            self.busy_add = False
                        self.update_last_seen(msg)
                        self.version = int(msg.version) + 1
                        self.external_channel.forward(origin_message)

                    # Let's begin our selfish control, but first we want to have a rest just to have a small delay
                    # This control is necessary to understand if our messages were kicked out from the list cycle
                    time.sleep(1)
                    if self.last_dead_message != '' and version_random_priority_check(msg, self.last_dead_message):
                        self.update_last_seen(msg)
                        self.version = int(msg.version) + 1
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
                                self.version = int(msg.version) + 1
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
                        self.version = int(msg.version) + 1
                        self.last_added_message.version = self.version
                        string_message = dumps(self.last_added_message)
                        self.external_channel.forward(string_message)

                    if self.last_restored_message != '' and \
                            version_random_priority_check(msg, self.last_restored_message):
                        self.update_last_seen(msg)
                        self.version = int(msg.version) + 1
                        self.last_restored_message.version = self.version
                        string_message = dumps(self.last_restored_message)
                        self.external_channel.forward(string_message)
                elif int(msg.version) == int(self.last_seen_version):
                    if int(self.last_seen_priority) > int(msg.priority):
                        self.last_seen_random = msg.random
                        self.logger.debug("this message from {} can be forwarded due to higher priority than {}\n[}".
                                          format(msg.source_id, self.last_seen_priority, msg.printable_message()))
                        self.last_seen_priority = msg.priority
                        self.external_channel.forward(dumps(msg))
                    elif int(self.last_seen_priority) < int(msg.priority):
                        self.logger.debug("this message from {} can't be forwarded due to lower priority than {}\n{}".
                                          format(msg.source_id, self.last_seen_priority, msg.printable_message()))
                    elif int(self.last_seen_priority) == int(msg.priority):
                        if int(self.last_seen_random) < int(msg.random):
                            self.logger.debug("this message from {} can be forwarded due to higher random than {}\n{}".
                                              format(msg.source_id, self.last_seen_random, msg.printable_message()))
                            self.last_seen_random = msg.random
                            self.external_channel.forward(dumps(msg))
                        else:
                            self.logger.debug("this message from {} can't be forwarded due to lower random than {}\n{}".
                                              format(msg.source_id, self.last_seen_random, msg.printable_message()))
                else:
                    self.logger.debug("this message will never be forwarded :\n"+msg.printable_message())


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
            return Node(data[ID], '', int_port,
                        ext_port, min_key=data[MIN_KEY], max_key=data[MAX_KEY])
        else:
            # int_port = "558{}".format(len("172.31.20."))
            # ext_port = "559{}".format(len("172.31.20."))
            int_port = "558{}".format(data[ID])
            ext_port = "559{}".format(data[ID])
            return Node(data[ID], data[IP], int_port,
                        ext_port, min_key=data[MIN_KEY], max_key=data[MAX_KEY])

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

        reader = DeadReader(myself, master, slave, slave_of_slave, master_of_master, self.logger, self.settings,
                            thread_reader_name)
        writer = DeadWriter(myself, master, slave, slave_of_slave, master_of_master, self.logger, self.settings,
                            thread_writer_name)

        reader.start()
        writer.start()

        reader.join()
    # unused
    # def create_process(self):
    #     Process(name='ListCommunicationProcess', target=Generator._create_process_environment(self))


def gen(l, s, a):
    generator = Generator(logger=l, settings=s, json_arg=a)
    generator.create_process_environment()


def create_single_process(l, s, a):
    l.debug("CREATING NEW PROCESS")
    from multiprocessing import Process
    new_process = Process(name="Process-NewBorn", target=gen, args=(l, s, a, ))
    new_process.start()
