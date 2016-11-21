#! /usr/bin/env python

import threading

from CellCycle.ChainModule.MemoryObject import MemoryObject
from CellCycle.KeyCalcManager import keyCalcToCreateANewNode, keyCalcWhenMasterDies
from Const import *
from random import randint
from ChainList import ChainList
from Printer import this_is_the_thread_in_action
from Message import Message
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

    def print_relatives(self):
        rel = [self.myself, self.master, self.master_of_master, self.slave, self.slave_of_slave]
        to_print = ["myself", "master", "master_of_master", "slave", "slave_of_slave"]
        str_to_print = ''
        for x in xrange(len(rel)):
            key = to_print[x]
            val = rel[x]
            str_to_print += 'Node {}, id {}, keys {}\n'.format(key, val.id, val.get_min_max_key())
        self.logger.debug(str_to_print)

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

    def change_parents(self):
        """
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
        """
        my = self.node_list.get_value(self.myself.id)
        m = my.master
        s = my.slave
        mm = self.node_list.get_value(m.id).master
        ss = self.node_list.get_value(s.id).slave

        self.master = m
        self.slave = s
        self.master_of_master = mm
        self.slave_of_slave = ss

    # This function is the same as change_parents but more secure because takes info from the list
    def change_parents_from_list(self):
        result = self.node_list.get_value(self.myself.id)
        myself = result.target
        master = result.master
        slave = result.slave
        master_of_master = self.node_list.get_value(master.id).master
        slave_of_slave = self.node_list.get_value(slave.id).slave
        self.myself = myself
        self.slave = slave
        self.master = master
        self.master_of_master = master_of_master
        self.slave_of_slave = slave_of_slave

    def change_slave_to(self, target_node, target_slave):
        result = self.node_list.get_value(target_node)
        target_node = result.target
        target_master = result.master
        target_slave = self.node_list.get_value(target_slave).target

        self.node_list.add_node(target_node=target_node, target_master=target_master,
                                target_slave=target_slave)

    def get_memory_obj_from_new_node(self, msg):
        if self.is_my_new_master_of_master(msg):
            mm_m = self.node_list.get_value(self.master_of_master.id).master
            mm_mm = self.node_list.get_value(mm_m.id).master
            mem = MemoryObject(mm_mm, mm_m, self.master_of_master, self.master, self.myself)
            return keyCalcToCreateANewNode(mem)
        elif self.is_my_new_master(msg):
            mm_m = self.node_list.get_value(self.master_of_master.id).master
            mem = MemoryObject(mm_m, self.master_of_master, self.master, self.myself, self.slave)
            return keyCalcToCreateANewNode(mem)
        elif self.is_my_new_slave(msg):
            mem = MemoryObject(self.master_of_master, self.master, self.myself, self.slave, self.slave_of_slave)
            return keyCalcToCreateANewNode(mem)
        elif self.is_my_new_slave_of_slave(msg):
            ss_s = self.node_list.get_value(self.slave_of_slave.id).slave
            mem = MemoryObject(self.master, self.myself, self.slave, self.slave_of_slave, ss_s)
            return keyCalcToCreateANewNode(mem)
        else:
            return None

    # This function assume that we have at least 4 nodes
    # This function assume that we have just updated the list
    def distribute_my_own_added_keys(self, mm, new_node):
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

    def distribute_my_own_dead_keys(self, mm, new_node):
        if self.slave.id == new_node.id:
            self.master_of_master.change_keys(mm.myself.min_key, mm.master_of_master.max_key)
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
    def change_added_keys_to(self, target_node):
        result = self.node_list.get_value(target_node)
        myself_to_change = result.target
        master_to_change = result.master
        slave_to_change = result.slave
        master_of_master_result = self.node_list.get_value(master_to_change.id).master
        master_of_master_result = self.node_list.get_value(master_of_master_result.id)
        master_of_master_to_change = master_of_master_result.target
        slave_of_slave_result = self.node_list.get_value(slave_to_change.id).slave
        slave_of_slave_result = self.node_list.get_value(slave_of_slave_result.id)
        slave_of_slave_to_change = slave_of_slave_result.target

        memory_obj = MemoryObject(master_of_master_to_change, master_to_change, myself_to_change,
                                  slave_to_change, slave_of_slave_to_change)

        mm = keyCalcToCreateANewNode(memory_obj)

        self.logger.debug("i'm {}, these are my nodes to compute keys\n{}".
                          format(self.myself.id, memory_obj.print_elements()))
        self.logger.debug("i'm {}, these are my computed keys\n{}".format(self.myself.id, mm.print_computed_keys()))

        myself_to_change.change_keys(mm.myself.min_key, mm.myself.max_key)
        master_to_change.change_keys(mm.master.min_key, mm.master.max_key)
        slave_to_change.change_keys(mm.slave.min_key, mm.slave.max_key)
        master_of_master_to_change.change_keys(mm.master_of_master.min_key, mm.master_of_master.max_key)
        slave_of_slave_to_change.change_keys(mm.slave_of_slave.min_key, mm.slave_of_slave.max_key)

        self.logger.debug("i'm {}".format(self.myself.id))
        self.logger.debug("adding this node in list, id: {}, master: {}, slave: {}".
                          format(myself_to_change.id, master_to_change.id, slave_to_change.id))
        self.node_list.add_node(myself_to_change, master_to_change, slave_to_change)
        self.logger.debug("adding this node in list, id: {}, master: {}, slave: {}".
                          format(master_to_change.id, master_of_master_to_change.id, myself_to_change.id))
        self.node_list.add_node(master_to_change, master_of_master_to_change, myself_to_change)
        self.logger.debug("adding this node in list, id: {}, master: {}, slave: {}".
                          format(slave_to_change.id, myself_to_change.id, slave_of_slave_to_change.id))
        self.node_list.add_node(slave_to_change, myself_to_change, slave_of_slave_to_change)
        self.logger.debug("adding this node in list, id: {}, master: {}, slave: {}".
                          format(master_of_master_to_change.id, master_of_master_result.master.id, master_to_change.id))
        self.node_list.add_node(master_of_master_to_change, master_of_master_result.master, master_to_change)
        self.logger.debug("adding this node in list, id: {}, master: {}, slave: {}".
                          format(slave_of_slave_to_change.id, slave_to_change.id, slave_of_slave_result.slave.id))
        self.node_list.add_node(slave_of_slave_to_change, slave_to_change, slave_of_slave_result.slave)

    def change_dead_keys_to(self, target_node):
        result = self.node_list.get_value(target_node)
        myself_to_change = result.target
        master_to_change = result.master
        slave_to_change = result.slave
        master_of_master_result = self.node_list.get_value(master_to_change.id).master
        master_of_master_result = self.node_list.get_value(master_of_master_result.id)
        master_of_master_to_change = master_of_master_result.target
        slave_of_slave_result = self.node_list.get_value(slave_to_change.id).slave
        slave_of_slave_result = self.node_list.get_value(slave_of_slave_result.id)
        slave_of_slave_to_change = slave_of_slave_result.target

        memory_obj = MemoryObject(master_of_master_to_change, master_to_change, myself_to_change,
                                  slave_to_change, slave_of_slave_to_change)

        mm = keyCalcWhenMasterDies(memory_obj)

        myself_to_change.change_keys(mm.myself.min_key, mm.myself.max_key)
        slave_to_change.change_keys(mm.slave.min_key, mm.slave.max_key)
        master_of_master_to_change.change_keys(mm.master_of_master.min_key, mm.master_of_master.max_key)
        slave_of_slave_to_change.change_keys(mm.slave_of_slave.min_key, mm.slave_of_slave.max_key)

        self.node_list.add_node(myself_to_change, master_to_change, slave_to_change)
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
    def notify_memory_request_finished(channel_to_send):
        msg = Message()
        msg.source_flag = INT
        msg.version = ''
        msg.priority = MEMORY_REQUEST_FINISHED
        msg.random = randint(MIN_RANDOM, MAX_RANDOM)
        msg.target_id = ''
        msg.target_key = ''
        msg.target_addr = ''
        msg.target_relative_id = ''
        msg.source_id = ''
        channel_to_send.send_first_internal_channel_message(message=dumps(msg))
        channel_to_send.wait_int_message(dont_wait=False)

    @staticmethod
    def notify_memory_request_started(channel_to_send):
        msg = Message()
        msg.source_flag = INT
        msg.version = ''
        msg.priority = MEMORY_REQUEST_STARTED
        msg.random = randint(MIN_RANDOM, MAX_RANDOM)
        msg.target_id = ''
        msg.target_key = ''
        msg.target_addr = ''
        msg.target_relative_id = ''
        msg.source_id = ''
        channel_to_send.send_first_internal_channel_message(message=dumps(msg))
        channel_to_send.wait_int_message(dont_wait=False)

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
        msg.priority = SCALE_UP
        msg.random = ''
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
        msg.priority = SCALE_DOWN
        msg.random = ''
        msg.target_id = ''
        msg.target_key = ''
        msg.target_addr = ''
        msg.target_relative_id = ''
        msg.source_id = ''
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

    def make_restore_node_msg(self, target_id, target_addr, target_key, source_flag=INT, target_master_id=''):
        return self.make_node_msg(source_flag=source_flag, priority=RESTORE, target_id=target_id,
                                  target_addr=target_addr,
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

    def is_one_of_my_r_of_r(self, target_id):
        mm_result = self.node_list.get_value(self.master_of_master.id).master
        mmm_result = self.node_list.get_value(mm_result.id).master
        ss_result = self.node_list.get_value(self.slave_of_slave.id).slave
        sss_result = self.node_list.get_value(ss_result.id).slave

        return mm_result.id == target_id or \
            mmm_result.id == target_id or \
            ss_result.id == target_id or \
            sss_result.id == target_id

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

    def test_update(self, source_id, target_relative_id, node_to_add):
        target_master = self.node_list.get_value(source_id).target
        target_slave = self.node_list.get_value(target_relative_id).target
        # Add the new node in list
        self.add_in_list(target_node=node_to_add, target_master=target_master,
                         target_slave=target_slave)

        target_master = source_id
        target_slave = target_relative_id

        # Update the master node, the new master of target_slave is target_id
        self.change_master_to(target_node=target_slave, target_master=node_to_add.id)
        # Update the slave node, the new master of target_master is target_id
        self.change_slave_to(target_node=target_master, target_slave=node_to_add.id)

        self.logger.debug("this is my new list\n{}".format(self.node_list.print_list()))

    def test_remove(self, target_id, source_id, target_relative_id):
        self.change_dead_keys_to(source_id)
        target_id = target_id
        target_master = target_relative_id
        target_slave = source_id

        # Update the target ID
        self.update_list(target_node=target_id, target_master=target_master, target_slave=target_slave)
        # Update the master node, the new master of target_slave is target_master
        self.change_master_to(target_node=target_slave, target_master=target_master)
        # Update the slave node, the new slave of target_master is target_slave
        self.change_slave_to(target_node=target_master, target_slave=target_slave)

        # if this node is one of my relatives, let's update our static attributes
        if target_id == self.slave.id:
            self.slave = self.slave_of_slave
            self.slave_of_slave = self.node_list.get_value(self.slave_of_slave.id).slave

        if target_id == self.slave_of_slave.id:
            self.slave_of_slave = self.node_list.get_value(target_id).slave
        # No case of master.addr
        if target_id == self.master_of_master.id:
            self.master_of_master = self.node_list.get_value(target_id).master
        if self.is_one_of_my_relatives(target_id):
            self.busy_add = True
            self.logger.debug("now i'm busy : {} is DEAD".format(target_id))
            # if i'm involved i have to be busy
        self.remove_from_list(target_id)
        self.logger.debug("this is my new list\n{}".format(self.node_list.print_list()))


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
