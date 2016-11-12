class Message:

    def __init__(self):
        self.source_flag = ''
        self.version = 0
        self.priority = ''
        self.random = 0
        self.target_id = ''
        self.target_addr = ''
        self.target_key = ''
        self.target_relative_id = ''
        self.source_id = ''

    def printable_message(self):
        attributes = vars(self)
        return ''.join("%s: %s\n" % item for item in attributes.items())


class InProcMessage:

    def __init__(self):
        self.source_flag = ''
        self.priority = ''
        self.list = ''

    def printable_message(self):
        attributes = vars(self)
        return ''.join("%s: %s\n" % item for item in attributes.items())


class InformationMessage:

    def __init__(self, node_list, version, last_seen_version, last_seen_priority, last_seen_random):
        self.node_list = node_list
        self.version = version
        self.last_seen_version = last_seen_version
        self.last_seen_priority = last_seen_priority
        self.last_seen_random = last_seen_random




