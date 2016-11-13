#! /usr/bin/env python

import threading

from CellCycle.ChainModule.MemoryObject import MemoryObject
from CellCycle.KeyCalcManager import keyCalcToCreateANewNode
from Const import *
from random import randint
from ChainList import ChainList
from Printer import this_is_the_thread_in_action
from Message import Message, InProcMessage
from cPickle import dumps
from socket import getfqdn, gethostbyname


class ListThread (threading.Thread):

    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings, name):
        threading.Thread.__init__(self, name=name)

        self.settings = settings
        self.logger = logger
        self.myself = myself
        self.master = master
        self.slave = slave
        self.slave_of_slave = slave_of_slave
        self.master_of_master = master_of_master
        self.busy_add = False

        if self.myself.ip is None:
            ip = gethostbyname(getfqdn())
            self.myself.ip = ip
            self.int_addr = '{}:{}'.format(ip, self.myself.int_port)    # ip:int_port
            self.ext_addr = '{}:{}'.format(ip, self.myself.ext_port)    # ip:int_port

        self.node_list = ChainList()
        self.add_in_list(myself, master, slave)
        self.add_in_list(master, master_of_master, myself)
        self.add_in_list(slave, myself, slave_of_slave)
        self.add_in_list(slave_of_slave, slave, master_of_master)
        self.add_in_list(master_of_master, slave_of_slave, master)

        self.list_communication = None

    def run(self):
        self.logger.debug(this_is_the_thread_in_action(self.myself.id))

    def canonical_check(self):
        return self.myself.ip in CANONICAL_ADDR

    def add_in_list(self, target_node, target_master, target_slave):
        self.node_list.add_node(target_node, target_master, target_slave)

    def update_list(self, target_node, target_master, target_slave):
        target_node = self.node_list.get_value(target_node).target
        target_master = self.node_list.get_value(target_master).target
        target_slave = self.node_list.get_value(target_slave).target

        self.node_list.add_node(target_node=target_node, target_master=target_master,
                                target_slave=target_slave)

    def change_parents(self, node_to_add):
        master_check = float(self.myself.id) > float(node_to_add.id) > float(self.master.id)
        slave_check = float(self.slave.id) > float(node_to_add.id) > float(self.myself.id)
        master_of_master_check = float(self.master.id) > float(node_to_add.id) > float(self.master_of_master.id)
        slave_of_slave_check = float(self.slave_of_slave.id) > float(node_to_add.id) > float(self.slave.id)

        if master_check:
            self.master = node_to_add
            self.logger.debug("my master is changed, now is {}".format(self.master.id))
        elif master_of_master_check:
            self.master_of_master = node_to_add
            self.logger.debug("my master_of_master is changed, now is {}".format(self.master_of_master.id))
        elif slave_check:
            self.slave = node_to_add
            self.logger.debug("my slave is changed, now is {}".format(self.slave.id))
        elif slave_of_slave_check:
            self.slave_of_slave = node_to_add
            self.logger.debug("my slave_of_slave is changed, now is {}".format(self.slave_of_slave.id))

    def change_slave_to(self, target_node, target_slave):
        result = self.node_list.get_value(target_node)
        target_node = result.target
        target_master = result.master
        target_slave = self.node_list.get_value(target_slave).target

        self.node_list.add_node(target_node=target_node, target_master=target_master,
                                target_slave=target_slave)

    # This function assume that we have at least 4 nodes
    # This function assume that we have just updated the list
    def distribute_my_own_keys(self, mm, new_node):
        if self.slave.id == new_node.id:
            self.master_of_master.change_keys(mm.master_of_master.min_key, mm.master_of_master.max_key)
            self.master.change_keys(mm.master.min_key, mm.master.max_key)
            self.myself.change_keys(mm.myself.min_key, mm.myself.max_key)
            self.slave_of_slave.change_keys(mm.slave.min_key, mm.slave.max_key)
        elif self.master.id == new_node.id:
            self.master_of_master.change_keys(mm.myself.min_key, mm.myself.max_key)
            self.myself.change_keys(mm.slave.min_key, mm.slave.max_key)
            self.slave.change_keys(mm.slave_of_slave.min_key, mm.slave_of_slave.max_key)
        elif self.master_of_master.id == new_node.id:
                self.master.change_keys(mm.slave.min_key, mm.slave.max_key)
                self.myself.change_keys(mm.slave_of_slave.min_key, mm.slave_of_slave.max_key)
        elif self.slave_of_slave.id == new_node.id:
                self.slave.change_keys(mm.myself.min_key, mm.myself.max_key)
                self.myself.change_keys(mm.master_of_master.min_key, mm.master_of_master.max_key)

    # This function search for a node in the list and changes all the 5 keys
    # This function must be called before the update of the list
    def change_keys_to(self, target_node):
        result = self.node_list.get_value(target_node)
        myself_to_change = result.target
        master_to_change = result.master
        slave_to_change = result.slave
        master_of_master_result = self.node_list.get_value(master_to_change.id)
        master_of_master_to_change = master_of_master_result.target
        slave_of_slave_result = self.node_list.get_value(slave_to_change.id)
        slave_of_slave_to_change = slave_of_slave_result.target

        memory_obj = MemoryObject(master_of_master_to_change, master_to_change, myself_to_change,
                                  slave_to_change, slave_of_slave_to_change)

        mm = keyCalcToCreateANewNode(memory_obj)

        myself_to_change.change_keys(mm.myself.min_key, mm.myself.max_key)
        master_to_change.change_keys(mm.master.min_key, mm.master.max_key)
        slave_to_change.change_keys(mm.slave.min_key, mm.slave.max_key)
        master_of_master_to_change.change_keys(mm.master_of_master.min_key, mm.master_of_master.max_key)
        slave_of_slave_to_change.change_keys(mm.slave_of_slave.min_key, mm.slave_of_slave.max_key)

        self.node_list.add_node(myself_to_change, master_to_change, slave_to_change)
        self.node_list.add_node(master_to_change, master_of_master_to_change, myself_to_change)
        self.node_list.add_node(slave_to_change, myself_to_change, slave_of_slave_to_change)
        self.node_list.add_node(master_of_master_to_change, master_of_master_result.master, master_to_change)
        self.node_list.add_node(slave_of_slave_to_change, slave_to_change, slave_of_slave_result.slave)

    def change_master_to(self, target_node, target_master):
        result = self.node_list.get_value(target_node)
        target_node = result.target
        target_slave = result.slave
        target_master = self.node_list.get_value(target_master).target

        self.node_list.add_node(target_node=target_node, target_master=target_master,
                                target_slave=target_slave)

    def make_node_msg(self, source_flag=INT, version='', priority='', target_id='', target_addr='', target_key='',
                      target_relative='', source_id=''):
        msg = Message()
        msg.source_flag = source_flag
        msg.version = version
        msg.priority = priority
        msg.random = randint(MIN_RANDOM, MAX_RANDOM)
        msg.target_id = target_id
        msg.target_key = target_key
        msg.target_addr = target_addr
        msg.target_relative_id = target_relative
        if source_id == '':
            msg.source_id = self.myself.id
        else:
            msg.source_id = source_id
        return msg

    @staticmethod
    def notify_restored(channel_to_send):
        msg = Message()
        msg.source_flag = INT
        msg.version = ''
        msg.priority = RESTORED
        msg.random = randint(MIN_RANDOM, MAX_RANDOM)
        msg.target_id = ''
        msg.target_key = ''
        msg.target_addr = ''
        msg.target_relative_id = ''
        msg.source_id = ''
        channel_to_send.send_first_internal_channel_message(message=dumps(msg))
        channel_to_send.wait_int_message(dont_wait=False)

    # This function is used by Memory Management Process to notify a new scale up
    # It is just a wrapper
    @staticmethod
    def notify_scale_up(channel_to_send):
        # new_id = compute_son_id(master_id=float(self.myself.id), slave_id=float(self.slave.id))
        # new_key = compute_son_key()
        # return self.make_add_node_msg(target_id=new_id,
        #                               target_key='{}:{}'.format(self.myself.min_key, self.myself.max_key),
        #                               source_flag=INT,
        #                               target_slave_id=self.myself.id)
        msg = Message()
        msg.source_flag = INT
        msg.version = ''
        msg.priority = ADD
        msg.random = randint(MIN_RANDOM, MAX_RANDOM)
        msg.target_id = ''
        msg.target_key = ''
        msg.target_addr = ''
        msg.target_relative_id = ''
        msg.source_id = ''
        channel_to_send.send_first_internal_channel_message(dumps(msg))
        channel_to_send.wait_int_message(dont_wait=False)

    # This function is used by Memory Management Process to notify a new scale up
    # It is just a wrapper

    @staticmethod
    def notify_scale_down(channel_to_send):
        # return self.make_dead_node_msg(target_id=self.myself.id, target_key=self.myself.key,
        #                                source_flag=INT, target_master_id=self.master.id, target_addr=self.myself.ip)
        msg = Message()
        msg.source_flag = INT
        msg.version = ''
        msg.priority = DEAD
        msg.random = randint(MIN_RANDOM, MAX_RANDOM)
        msg.target_id = ''
        msg.target_key = ''
        msg.target_addr = ''
        msg.target_relative_id = ''
        msg.source_id = ''
        channel_to_send.send_first_internal_channel_message(dumps(msg))
        channel_to_send.wait_int_message(dont_wait=False)

    def notify_list(self, channel_to_send):
        # return self.make_dead_node_msg(target_id=self.myself.id, target_key=self.myself.key,
        #                                source_flag=INT, target_master_id=self.master.id, target_addr=self.myself.ip)
        msg = InProcMessage()
        msg.source_flag = INT
        msg.list = self.node_list
        msg.priority = IN_PROC
        self.logger.debug("sending list to {}".format(self.myself.id))
        channel_to_send.send_first_internal_channel_message(dumps(msg))
        channel_to_send.wait_int_message(dont_wait=False)

    def make_alive_node_msg(self, target_id, target_master_id, source_flag=INT):
        return self.make_node_msg(source_flag, priority=ALIVE, target_id=target_id, target_addr='',
                                  target_relative=target_master_id)

    def make_added_node_msg(self, target_id, target_addr, target_key, source_flag=INT, target_slave_id='',
                            source_id=''):
        return self.make_node_msg(source_flag=source_flag, priority=ADDED, target_id=target_id,
                                  target_addr=target_addr,
                                  target_key=target_key,
                                  target_relative=target_slave_id, source_id=source_id)

    def make_add_node_msg(self, target_id, target_key, source_flag=INT, target_slave_id=''):
        return self.make_node_msg(source_flag=source_flag, priority=ADD, target_id=target_id, target_addr='',
                                  target_key=target_key,
                                  target_relative=target_slave_id)

    def make_dead_node_msg(self, target_id, target_addr, target_key, source_flag=INT, target_master_id=''):
        return self.make_node_msg(source_flag=source_flag, priority=DEAD, target_id=target_id, target_addr=target_addr,
                                  target_key=target_key,
                                  target_relative=target_master_id)

    def make_restored_node_msg(self, target_id, target_addr, target_key, source_flag=INT, target_master_id=''):
        return self.make_node_msg(source_flag=source_flag, priority=RESTORED,
                                  target_id=target_id, target_addr=target_addr,
                                  target_key=target_key, target_relative=target_master_id)

    def is_one_of_my_relatives(self, target_id):
        return self.master_of_master.id == target_id or \
            self.master.id == target_id or \
            self.slave.id == target_id or \
            self.slave_of_slave.id == target_id

    def is_my_new_slave_of_slave(self, message):
        return float(self.slave_of_slave.id) > float(message.target_id) > float(self.slave.id)

    def is_my_new_master_of_master(self, message):
        return float(self.master.id) > float(message.target_id) > float(self.master_of_master.id)

    def is_my_new_master(self, message):
        return float(self.myself.id) > float(message.target_id) > float(self.master.id)

    def is_my_new_slave(self, message):
        return float(self.myself.id) < float(message.target_id) < float(self.slave.id)

    # Remove an obsolete node from the list
    def remove_from_list(self, target_id):
        try:
            self.node_list.remove_node(target_id)
        except KeyError:
            raise KeyError

    # Check if the node is in list
    def is_in_list(self, message):
        return self.node_list.is_in_list(message.target_id)

    # Get a node from the list, if it exists
    def get_target_id(self, target_id):
        try:
            return self.node_list.get_value(target_id)
        except KeyError:
            raise KeyError

    # Get an ip from a specific key, used by memory thread
    def get_ip_from_key(self, key_to_find):
        node_result = self.node_list.find_memory_key(key_to_find)
        if node_result is not None:
            return node_result.target.ip
        else:
            return None


class Node:

    def __init__(self, node_id, ip, int_port, ext_port, min_key, max_key, memory_port=''):
        self.id = str(node_id)  # Node ID
        if ip is not None:
            self.int_addr = '{}:{}'.format(ip, int_port)    # ip:int_port
            self.ext_addr = '{}:{}'.format(ip, ext_port)    # ip:ext_port
        self.min_key = str(min_key)     # Min memory key
        self.max_key = str(max_key)     # Max memory key
        self.ip = ip    # Node IP
        self.int_port = int_port    # Node internal channel's port
        self.ext_port = ext_port    # Node external channel's port
        self.memory_port = memory_port

    def get_min_max_key(self):
        return "{}:{}".format(self.min_key, self.max_key)

    @staticmethod
    def to_min_max_key_obj(min_max_string):
        min_max_split = min_max_string.split(':')
        return Key(min_max_split[0], min_max_split[1])

    def change_keys(self, min_key, max_key):
        self.min_key = str(min_key)
        self.max_key = str(max_key)

    def print_values(self):
        return ''.join('{}, {}\n'.format(key, val) for key, val in self.__dict__.items())


class Key:

    def __init__(self, min_key, max_key):
        self.min_key = min_key
        self.max_key = max_key
