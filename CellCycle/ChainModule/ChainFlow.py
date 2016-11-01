from Const import *
from Message import Message

# Object - String Message Conversion


def from_ext_msg_string_to_msg_obj(msg):
    split = msg.split()
    obj = Message()
    obj.source_flag = split[SOURCE_FLAG_INDEX]
    obj.version = split[VERSION_INDEX]
    obj.priority = split[PRIORITY_INDEX]
    obj.random = split[RANDOM_INDEX]
    obj.target_id = split[TARGET_ID_INDEX]
    obj.target_key = split[TARGET_KEY_INDEX]
    obj.source_id = split[SOURCE_ID_INDEX]

    return obj


def from_int_msg_string_to_msg_obj(msg):
    split = msg.split()
    obj = Message()
    obj.source_flag = split[SOURCE_FLAG_INDEX]
    obj.version = NO_VERSION
    obj.priority = split[PRIORITY_INDEX-1]
    obj.random = split[RANDOM_INDEX-1]
    obj.target_id = split[TARGET_ID_INDEX-1]
    obj.target_key = split[TARGET_KEY_INDEX-1]
    obj.source_id = split[SOURCE_ID_INDEX-1]

    return obj


def from_ext_alive_msg_string_to_alive_msg_obj(msg):
    split = msg.split()
    obj = Message()
    obj.source_flag = split[SOURCE_FLAG_INDEX]
    obj.priority = split[PRIORITY_INDEX-1]
    obj.target_id = split[TARGET_ID_INDEX-2]

    return obj


def from_msg_string_to_msg_obj(msg, source_flag=EXT):
    if source_flag == INT:
        return from_int_msg_string_to_msg_obj(msg)
    else:
        return from_ext_msg_string_to_msg_obj(msg)

# Return a string with EXT flag and the right version


def from_msg_obj_to_string(message):
    msg = dict()
    msg[SOURCE_FLAG_INDEX] = message.source_flag
    msg[VERSION_INDEX] = message.version
    msg[PRIORITY_INDEX] = message.priority
    msg[RANDOM_INDEX] = message.random
    msg[TARGET_ID_INDEX] = message.target_id
    msg[TARGET_KEY_INDEX] = message.target_key
    msg[SOURCE_ID_INDEX] = message.source_id

    return ' '.join(str(x) for x in msg.values())

# Make Node Message


# Return a string with EXT flag and the right version
def to_external_string_message(version, message):
    ext_msg = to_external_obj_message(version, message)
    return from_msg_obj_to_string(ext_msg)


# Return an obj with EXT flag and the right version
def to_external_obj_message(version, message):
    message.source_flag = EXT
    message.version = version
    return message

# Reply

# Forward

# Message Flow


def msg_variable_version_check(msg, version):
    return msg.version >= version


def msg_msg_version_check(msg1, msg2):
    return msg1.version - msg2.version


def msg_msg_priority_check(msg1, msg2):
    return msg1.priority - msg2.priority


def msg_msg_random_check(msg1, msg2):
    return msg1.random - msg2.random


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
    return msg[SOURCE_FLAG_INDEX] == source_flag


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
