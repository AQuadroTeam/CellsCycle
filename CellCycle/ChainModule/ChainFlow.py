from Const import *
from cPickle import dumps


# Return an obj with EXT flag and the right version
def to_external_message(version, message):
    message.source_flag = EXT
    message.version = str(version)
    return message

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
    if msg2 != '':
        return dumps(msg1) == dumps(msg2)
    else:
        return False


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


def is_inproc_message(msg):
    return check_message_priority(msg, IN_PROC)


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
