#! /usr/bin/env python

import threading
from Const import *
from random import randint
from ChainList import ChainList
from Printer import this_is_the_thread_in_action
from ChainFlow import compute_son_id
from Message import Message


class ListThread (threading.Thread):

    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings):
        threading.Thread.__init__(self)

        self.settings = settings
        self.logger = logger
        self.myself = myself
        self.master = master
        self.slave = slave
        self.slave_of_slave = slave_of_slave
        self.master_of_master = master_of_master
        self.busy_add = False

        self.node_list = ChainList()
        # TODO this is for just 5 nodes
        self.add_in_list(myself, master, slave)
        self.add_in_list(master, master_of_master, myself)
        self.add_in_list(slave, myself, slave_of_slave)
        self.add_in_list(slave_of_slave, slave, master_of_master)
        self.add_in_list(master_of_master, slave_of_slave, master)

        self.list_communication = None

    def run(self):
        self.logger.debug(this_is_the_thread_in_action(self.myself.id))

    def add_in_list(self, target_node, target_master, target_slave):
        self.node_list.add_node(target_node, target_master, target_slave)

    def update_list(self, target_node, target_master, target_slave):
        target_node = self.node_list.get_value(target_node).target
        target_master = self.node_list.get_value(target_master).target
        target_slave = self.node_list.get_value(target_slave).target

        self.node_list.add_node(target_node=target_node, target_master=target_master,
                                target_slave=target_slave)

    def change_slave_to(self, target_node, target_slave):
        result = self.node_list.get_value(target_node)
        target_node = result.target
        target_master = result.master
        target_slave = self.node_list.get_value(target_slave)

        self.node_list.add_node(target_node=target_node, target_master=target_master,
                                target_slave=target_slave)

    def change_master_to(self, target_node, target_master):
        result = self.node_list.get_value(target_node)
        target_node = result.target
        target_slave = result.slave
        target_master = self.node_list.get_value(target_master)

        self.node_list.add_node(target_node=target_node, target_master=target_master,
                                target_slave=target_slave)

    def make_node_msg(self, source_flag=INT, version='', priority='', target_id='', target_addr='', target_key='',
                      target_relative=''):
        msg = Message()
        msg.source_flag = source_flag
        msg.version = version
        msg.priority = priority
        msg.random = randint(MIN_RANDOM, MAX_RANDOM)
        msg.target_id = target_id
        msg.target_key = target_key
        msg.target_addr = target_addr
        msg.target_relative_id = target_relative
        msg.source_id = self.myself.id

        return msg

    # This function is used by Memory Management Process to notify a new scale up
    # It is just a wrapper
    def notify_scale_up(self):
        new_id = compute_son_id(master_id=float(self.myself.id), slave_id=float(self.slave.id))
        # new_key = compute_son_key()
        return self.make_add_node_msg(target_id=new_id,
                                      target_key='{}:{}'.format(self.myself.min_key, self.myself.max_key),
                                      source_flag=INT,
                                      target_slave_id=self.myself.id)

    # This function is used by Memory Management Process to notify a new scale up
    # It is just a wrapper
    def notify_scale_down(self):
        return self.make_dead_node_msg(target_id=self.myself.id, target_key=self.myself.key,
                                       source_flag=INT, target_master_id=self.master.id, target_addr=self.myself.ip)

    def make_alive_node_msg(self, target_id, target_master_id, source_flag=INT):
        return self.make_node_msg(source_flag, priority=ALIVE, target_id=target_id, target_addr='',
                                  target_relative=target_master_id)

    def make_added_node_msg(self, target_id, target_addr, target_key, source_flag=INT, target_slave_id=''):
        return self.make_node_msg(source_flag=source_flag, priority=ADDED, target_id=target_id, target_addr=target_addr,
                                  target_key=target_key,
                                  target_relative=target_slave_id)

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

    def is_my_new_master(self, message):
        return self.myself.id > message.target_id > self.master.id

    def is_my_new_slave(self, message):
        return self.myself.id < message.target_id < self.slave.id

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

    def __init__(self, node_id, ip, int_port, ext_port, min_key, max_key):
        self.id = str(node_id)  # Node ID
        self.int_addr = '{}:{}'.format(ip, int_port)    # ip:int_port
        self.ext_addr = '{}:{}'.format(ip, ext_port)    # ip:ext_port
        self.min_key = str(min_key)     # Min memory key
        self.max_key = str(max_key)     # Max memory key
        self.ip = ip    # Node IP
        self.int_port = int_port    # Node internal channel's port
        self.ext_port = ext_port    # Node external channel's port

    def get_min_max_key(self):
        return "{}:{}".format(self.min_key, self.max_key)

    @staticmethod
    def to_min_max_key_obj(min_max_string):
        min_max_split = min_max_string.split(':')
        return Key(min_max_split[0], min_max_split[1])


class Key:

    def __init__(self, min_key, max_key):
        self.min_key = min_key
        self.max_key = max_key