from Const import *
from math import ceil

'''There are two standard behaviour for requester to name a new child, depends on name of the Slave node of the creator.
If the greater whole number of Slave id and Requester id are the same (e.g. 3.1 and 3.999 or 3.4 and 4):
    Name new node with float (Requester id + (Slave id - Requester id)/2 )
Else:
    Name new node with the greater whole number of Requester Id

This naming behaviour is needed to maintain the total order relationship between nodes,
other structures as P2P Chord use a PseudoRandom Generator to name new nodes,
and generate a new random number between two ids, using high value numbers,
hoping there wont be consecutive ids (this solution can be easily avoided with our method).
'''


def compute_son_id(master_id, slave_id):   # Computes a new id based on greater whole number
    # assert(master_id < master_id)

    master_greater_whole_number = ceil(master_id)
    if master_greater_whole_number == master_id:
        master_greater_whole_number += 1

    slave_greater_whole_number = ceil(slave_id)

    if master_greater_whole_number == slave_greater_whole_number:
        return float(master_id + (slave_id - master_id)/2.0)
    else:
        return master_greater_whole_number


def compute_son_key():
    pass


# Return an obj with EXT flag and the right version
def to_external_message(version, message):
    message.source_flag = EXT
    message.version = str(version)
    return message

# Reply

# Forward

# Message Flow


def msg_variable_version_check(msg, version):
    return int(msg.version) >= version


def msg_msg_version_check(msg1, msg2):
    return int(msg1.version) - int(msg2.version)


def msg_msg_priority_check(msg1, msg2):
    return int(msg1.priority) - int(msg2.priority)


def msg_msg_random_check(msg1, msg2):
    return int(msg1.random) - int(msg2.random)


def is_equal_message(msg1, msg2):
    return msg1 == msg2


def is_my_last_add_message(msg, last_add_message):
    return is_equal_message(msg, last_add_message)


def is_my_last_added_message(msg, last_added_message):
    return is_equal_message(msg, last_added_message)


def is_my_last_dead_message(msg, last_dead_message):
    return is_equal_message(msg, last_dead_message)


def is_my_last_restored_message(msg, last_restored_message):
    return is_equal_message(msg, last_restored_message)


def version_random_priority_check(new_message, old_message):
    version_diff = msg_msg_version_check(new_message, old_message)
    if version_diff > 0:  # new_version > old_message
        return True
    elif version_diff == 0:  # new_version == old_message
        priority_diff = msg_msg_priority_check(new_message, old_message)
        if priority_diff > 0:  # new_priority > old_priority
            return True
        elif priority_diff == 0:
            random_diff = msg_msg_random_check(new_message, old_message)
            return random_diff > 0  # new_random > old_random
        else:
            return False
    else:
        return False

# Message Source


# In this phase we don't now which is the type of message
def check_source_message(msg, source_flag):
    return msg.source_flag == source_flag


def is_int_message(msg):
    return check_source_message(msg, INT)


def is_ext_message(msg):
    return check_source_message(msg, EXT)

# Message Priority


def check_message_priority(msg, priority):
    return msg.priority == priority


def is_alive_message(msg):
    return check_message_priority(msg, ALIVE)


def is_add_message(msg):
    return check_message_priority(msg, ADD)


def is_added_message(msg):
    return check_message_priority(msg, ADDED)


def is_restored_message(msg):
    return check_message_priority(msg, RESTORED)


def is_dead_message(msg):
    return check_message_priority(msg, DEAD)

# Check Dead Stuff


def is_dead_and_i_am_the_target(msg, target_id):
    return msg.priority == DEAD and msg.target_id == target_id
