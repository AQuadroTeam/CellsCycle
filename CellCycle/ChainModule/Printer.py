#! /usr/bin/env python
from ListCommunication import Address

# Just a few methods to print better

SOMETHING_WENT_WRONG = 'Error sending the message, something went wrong'
IS_THE_SERVER_STILL_RUNNING = 'Error sending the message, is the server still running?'
NOTHING_TO_RECEIVE = 'Nothing to receive'


def format_k_args(string_to_format, k):
    return string_to_format.format(*k)


def these_are_my_features_writer(myself_id, master_id, slave_id):
    k = [myself_id, master_id, slave_id]
    return format_k_args("These are my features: (Writer {}) Master ID : {} , SlaveID: {}", k)


def these_are_my_features_reader(myself_id, master_id, slave_id):
    k = [myself_id, master_id, slave_id]
    return format_k_args("These are my features: (Reader {}) Master ID : {} , SlaveID: {}", k)


def starting_writer(node_id):
    k = [node_id]
    return format_k_args("Starting Writer {}", k)


def exiting_writer(node_id):
    k = [node_id]
    return format_k_args("Exiting Writer {}", k)


def starting_reader(node_id):
    k = [node_id]
    return format_k_args("Starting Reader {}", k)


def exiting_reader(node_id):
    k = [node_id]
    return format_k_args("Exiting Reader {}", k)


def waiting_sync(myself_id, slave_id, complete_address):
    k = [myself_id, slave_id, complete_address]
    return format_k_args("Writer {} waiting for sync with node {} with address {}", k)


def sync_completed(myself_id, slave_id, complete_address):
    k = myself_id, slave_id, complete_address
    return format_k_args("Sync completed. New client socket (Writer {}) to node {} with address {}", k)


def i_am_dead_goodbye(myself_id):
    k = [myself_id]
    return format_k_args('Ok i\'m DEAD.. {} Goodbye everyone!', k)


def new_node_added(myself_id):
    k = [myself_id]
    return format_k_args('New node added, i\'m Reader {}', k)


def just_received_new_msg(myself_id, master_id, message):
    k = [myself_id, master_id, message]
    return format_k_args("I'm a READER FOR A DEAD {}, i've just received this message from my master {} : {}", k)


def your_dead_dear(myself, master_id):
    k = [myself, master_id]
    return format_k_args("I\'m {} and you\'re dead dear {}, just remove you from the list and reset the socket", k)


def this_is_my_dead_message(myself, master_id, message):
    k = [myself, master_id, message]
    return format_k_args("I'm {} and my master {} is dead. This is my dead_message : {}", k)


def send_i_am_alive(myself, slave_id):
    k = [myself, slave_id]
    return format_k_args("Send that i'm ALIVE ({}) to {}", k)


def something_went_wrong():
    return SOMETHING_WENT_WRONG


def is_the_server_still_running():
    return IS_THE_SERVER_STILL_RUNNING


def nothing_to_receive():
    return NOTHING_TO_RECEIVE


def this_is_my_item(myself_id, item):
    k = [myself_id, item]
    return format_k_args("This is my item (Writer {}): {}", k)


def closing_socket_with(complete_address):
    k = [complete_address]
    return format_k_args("Closing socket with {}", k)


def generating_server_connection_point(complete_address):
    k = [complete_address]
    return format_k_args("Generating server connection point {}", k)


def generating_client_connection_point(complete_address):
    k = [complete_address]
    return format_k_args("Generating client connection point {}", k)


def this_is_the_thread_in_action(thread_in_action):
    k = [thread_in_action]
    return format_k_args("This is the thread {} in action.", k)


def dictionary_to_string(dictionary):
    return ''.join('{}{}'.format(key, val) for key, val in dictionary.items())


def from_complete_address_to_ip_port(complete_address):
    address_split = complete_address.split(':')
    ip = address_split[0]
    port = address_split[1]
    return Address(ip, port)

