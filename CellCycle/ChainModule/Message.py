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
