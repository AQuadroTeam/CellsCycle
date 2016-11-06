from CellCycle.ChainModule.ListThread import ListThread, Node
from start import loadSettingsAndLogger
from CellCycle.ChainModule.ChainFlow import *

TEST_ADDRESS = '172.0.0.1'


class ListThreadTest(ListThread):

    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings):
        ListThread.__init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings)

    def run(self):
        messages = []

        alive_msg = self.make_alive_node_msg(self.myself.id, self.master.id)
        messages.append(alive_msg)
        dead_message = self.make_dead_node_msg(target_id=self.master.id, target_addr=self.master.ip,
                                               target_key=self.master.get_min_max_key(),
                                               target_master_id=self.master_of_master.id)
        messages.append(dead_message)

        # Suppose that we want to scale up
        add_message = self.notify_scale_up()
        messages.append(add_message)

        min_max_key = self.master.get_min_max_key()
        added_message = self.make_added_node_msg(target_id=self.master.id,
                                                 target_key=min_max_key,
                                                 target_addr=self.master.ip,
                                                 target_slave_id=self.slave.id)
        messages.append(added_message)

        restored_message = self.make_restored_node_msg(target_id=self.myself.id, target_addr=self.myself.ip,
                                                       target_key=self.myself.get_min_max_key(),
                                                       target_master_id=self.master.id)
        messages.append(restored_message)

        self.logger.debug("######## INT MESSAGES #######")
        self.logger.debug(alive_msg.printable_message())
        self.logger.debug(dead_message.printable_message())
        self.logger.debug(add_message.printable_message())
        self.logger.debug(added_message.printable_message())
        self.logger.debug(restored_message.printable_message())

        # self.print_ext_messages(messages)

        # Pretend that we have a dead node
        dead_message = self.make_dead_node_msg(target_id=self.master.id, target_addr=self.master.ip,
                                               target_key=self.master.get_min_max_key(),
                                               target_master_id=self.master_of_master.id)
        dead_message = to_external_message(version=1, message=dead_message)

        self.dead_test(dead_message)

        # Needs a change on find_memory_key
        # self.query_test(22)

    def dead_test(self, msg):
        self.logger.debug('###### DEAD TEST ########')
        self.logger.debug(is_dead_message(msg))
        self.logger.debug(not is_add_message(msg))
        self.logger.debug(not is_added_message(msg))
        self.logger.debug(not is_alive_message(msg))
        self.logger.debug(not is_restored_message(msg))
        self.logger.debug(is_dead_and_i_am_the_target(msg, target_id=self.master.id))
        self.logger.debug(is_ext_message(msg))
        self.logger.debug(not is_int_message(msg))

        # key_obj = Node.to_min_max_key_obj(msg.target_key)
        # node_to_check = Node(node_id=msg.target_id, ip=msg.target_addr, int_port=self.settings.getIntPort(),
        #                      ext_port=self.settings.getExtPort(), min_key=key_obj.min_key,
        #                      max_key=key_obj.max_key)

        self.logger.debug(self.is_in_list(msg))
        self.logger.debug(not self.is_my_new_master(msg))
        self.logger.debug(not self.is_my_new_slave(msg))
        self.logger.debug(self.is_one_of_my_relatives(msg.target_id))

    def print_ext_messages(self, messages):
        self.logger.debug("######## EXT MESSAGES #######")

        for m in messages:
            m = to_external_message(1, m)
            self.logger.debug(m.printable_message())

    def query_test(self, key_to_find):
        self.logger.debug('###### KEY TO FIND TEST ########')
        self.logger.debug(self.get_ip_from_key(key_to_find=key_to_find).target.id == '2')

CONFIG_PATH = "/home/alessandro/git/CellsCycle/config.txt"

loaded_settings, loaded_logger = loadSettingsAndLogger(CONFIG_PATH)

master_of_master_to_load = Node(1, TEST_ADDRESS, loaded_settings.getIntPort(), loaded_settings.getExtPort(), 0, 19)
master_to_load = Node(2, TEST_ADDRESS, loaded_settings.getIntPort(), loaded_settings.getExtPort(), 20, 39)
myself_to_load = Node(3, TEST_ADDRESS, loaded_settings.getIntPort(), loaded_settings.getExtPort(), 40, 59)
slave_to_load = Node(4, TEST_ADDRESS, loaded_settings.getIntPort(), loaded_settings.getExtPort(), 60, 79)
slave_of_slave_to_load = Node(5, TEST_ADDRESS, loaded_settings.getIntPort(), loaded_settings.getExtPort(), 80, 99)

list_thread_test = ListThreadTest(myself=myself_to_load, master=master_to_load,
                                  master_of_master=master_of_master_to_load, slave=slave_to_load,
                                  slave_of_slave=slave_of_slave_to_load, logger=loaded_logger, settings=loaded_settings)
list_thread_test.run()
