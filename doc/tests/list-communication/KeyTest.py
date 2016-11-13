from CellCycle.ChainModule.ListThread import *
from start import loadSettings
from start import loadLogger
from CellCycle.MemoryModule.calculateSon import calculateSonId


def add_check():

    currentProfile = {"profile_name": "alessandro_fazio", "key_pair": "AWSCellCycle", "branch": "ListUtilities"}
    settings_to_launch = loadSettings(currentProfile=currentProfile)
    logger_to_launch = loadLogger(settings_to_launch)

    n1 = Node("1", "172.10.1.1", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "0", "19")
    n2 = Node("2", "172.10.1.2", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "20", "39")
    n3 = Node("3", "172.10.1.3", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "40", "59")
    n4 = Node("4", "172.10.1.4", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "60", "79")
    n5 = Node("5", "172.10.1.5", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "80", "99")

    i3 = ListThread(master_of_master=n1, master=n2, myself=n3, slave=n4, slave_of_slave=n5, logger=logger_to_launch,
                    settings=settings_to_launch, name=n3.id)
    i4 = ListThread(master_of_master=n2, master=n3, myself=n4, slave=n5, slave_of_slave=n1, logger=logger_to_launch,
                    settings=settings_to_launch, name=n4.id)
    i5 = ListThread(master_of_master=n3, master=n4, myself=n5, slave=n1, slave_of_slave=n2, logger=logger_to_launch,
                    settings=settings_to_launch, name=n5.id)
    i1 = ListThread(master_of_master=n4, master=n5, myself=n1, slave=n2, slave_of_slave=n3, logger=logger_to_launch,
                    settings=settings_to_launch, name=n1.id)
    i2 = ListThread(master_of_master=n5, master=n1, myself=n2, slave=n3, slave_of_slave=n4, logger=logger_to_launch,
                    settings=settings_to_launch, name=n2.id)

    # pretend that we add the new node
    m_o = MemoryObject(n1, n2, n3, n4, n5)
    new_min_max_key = keyCalcToCreateANewNode(m_o).newNode

    new_node_id_to_add = str(calculateSonId(float(n3.id), float(n4.id)))
    new_node_instance_to_add = Node(new_node_id_to_add, None, settings_to_launch.getIntPort(),
                                    settings_to_launch.getExtPort(),
                                    new_min_max_key.min_key, new_min_max_key.max_key)

    '''
    logger_to_launch.debug("########## BEFORE ADD ############")
    i1.print_relatives()
    i2.print_relatives()
    i3.print_relatives()
    i4.print_relatives()
    i5.print_relatives()
    '''

    logger_to_launch.debug("########## AFTER ADD #############")

    i4.change_added_keys_to(n3.id)
    i4.test_update(source_id=n3.id, target_relative_id=n4.id, node_to_add=new_node_instance_to_add)
    i4.change_parents_from_list()
    i5.change_added_keys_to(n3.id)
    i5.test_update(source_id=n3.id, target_relative_id=n4.id, node_to_add=new_node_instance_to_add)
    i5.change_parents_from_list()
    i1.change_added_keys_to(n3.id)
    i1.test_update(source_id=n3.id, target_relative_id=n4.id, node_to_add=new_node_instance_to_add)
    i1.change_parents_from_list()
    i2.change_added_keys_to(n3.id)
    i2.test_update(source_id=n3.id, target_relative_id=n4.id, node_to_add=new_node_instance_to_add)
    i2.change_parents_from_list()
    i3.change_added_keys_to(n3.id)
    i3.test_update(source_id=n3.id, target_relative_id=n4.id, node_to_add=new_node_instance_to_add)
    i3.change_parents_from_list()

    i1.print_relatives()
    i2.print_relatives()
    i3.print_relatives()
    i4.print_relatives()
    i5.print_relatives()


def dead_check():

    currentProfile = {"profile_name": "alessandro_fazio", "key_pair": "AWSCellCycle", "branch": "ListUtilities"}
    settings_to_launch = loadSettings(currentProfile=currentProfile)
    logger_to_launch = loadLogger(settings_to_launch)

    n1 = Node("1", "172.10.1.1", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "12", "19")
    n2 = Node("2", "172.10.1.2", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "20", "39")
    n3 = Node("3", "172.10.1.3", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "40", "59")
    n4 = Node("4", "172.10.1.4", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "60", "79")
    n5 = Node("5", "172.10.1.5", settings_to_launch.getIntPort(), settings_to_launch.getExtPort(), "80", "11")

    i3 = ListThread(master_of_master=n1, master=n2, myself=n3, slave=n4, slave_of_slave=n5, logger=logger_to_launch,
                    settings=settings_to_launch, name=n3.id)
    i4 = ListThread(master_of_master=n2, master=n3, myself=n4, slave=n5, slave_of_slave=n1, logger=logger_to_launch,
                    settings=settings_to_launch, name=n4.id)
    i5 = ListThread(master_of_master=n3, master=n4, myself=n5, slave=n1, slave_of_slave=n2, logger=logger_to_launch,
                    settings=settings_to_launch, name=n5.id)
    i1 = ListThread(master_of_master=n4, master=n5, myself=n1, slave=n2, slave_of_slave=n3, logger=logger_to_launch,
                    settings=settings_to_launch, name=n1.id)

    '''
    logger_to_launch.debug("########## BEFORE ADD ############")
    i1.print_relatives()
    i2.print_relatives()
    i3.print_relatives()
    i4.print_relatives()
    i5.print_relatives()
    '''

    logger_to_launch.debug("########## AFTER DEAD #############")

    i4.change_dead_keys_to(n3.id)
    i4.test_remove(target_id=n2.id, source_id=n3.id, target_relative_id=n1.id)
    i4.change_parents_from_list()
    i5.change_dead_keys_to(n3.id)
    i5.test_remove(target_id=n2.id, source_id=n3.id, target_relative_id=n1.id)
    i5.change_parents_from_list()
    i1.change_dead_keys_to(n3.id)
    i1.test_remove(target_id=n2.id, source_id=n3.id, target_relative_id=n1.id)
    i1.change_parents_from_list()
    i3.change_dead_keys_to(n3.id)
    i3.test_remove(target_id=n2.id, source_id=n3.id, target_relative_id=n1.id)
    i3.change_parents_from_list()

    i1.print_relatives()
    i3.print_relatives()
    i4.print_relatives()
    i5.print_relatives()

    logger_to_launch.debug("this is the ip found {}".format((i1.node_list.find_memory_key(0)).target.ip))
