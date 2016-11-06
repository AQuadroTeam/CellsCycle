from CellCycle.ChainModule.ListThread import ListThread, Node
from start import loadSettingsAndLogger

TEST_ADDRESS = '172.0.0.1'


class ListThreadTest(ListThread):

    def __init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings):
        ListThread.__init__(self, myself, master, slave, slave_of_slave, master_of_master, logger, settings)

    def run(self):
        alive_msg = self.make_alive_node_msg(self.myself.id, self.master.id)
        self.logger.debug(alive_msg)

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
