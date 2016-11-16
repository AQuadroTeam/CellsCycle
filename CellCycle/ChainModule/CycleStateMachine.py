class State(object):

    def __init__(self, target_instance):
        self.target_instance = target_instance
        self.transitions = {"Free": self.from_free,
                            "BusyAddPS": self.from_busy_add_ps,
                            "BusyAddPL": self.from_busy_add_pl,
                            "BusyDeadPS": self.from_busy_dead_ps,
                            "BusyDeadPL": self.from_busy_dead_pl,
                            "MemoryRequest": self.from_memory_request}
        self._can_pass_add = None
        self._can_pass_restore = None
        self._can_scale_up = None
        self._can_scale_down = None
        self._can_restore = None
        self._ext_locked = None

    def __str__(self):
        return "I am in state {}".format(self.__class__.__name__)

    def ext_locked(self):
        return self._ext_locked

    def can_pass_add(self):
        return self._can_pass_add

    def can_pass_restore(self):
        return self._can_pass_restore

    def can_restore(self):
        return self._can_restore

    def can_scale_up(self):
        return self._can_scale_up

    def can_scale_down(self):
        return self._can_scale_down

    def get_name(self):
        return self.__class__.__name__

    def transfer_from(self, prev_state):
        return self.transitions[prev_state.__class__.__name__]()

    def from_busy_add_ps(self):
        pass

    def from_busy_add_pl(self):
        pass

    def from_busy_dead_ps(self):
        pass

    def from_busy_dead_pl(self):
        pass

    def from_free(self):
        pass

    def from_memory_request(self):
        pass


class Free(State):

    def __init__(self, target_instance):
        super(Free, self).__init__(target_instance)
        self._can_pass_add = True
        self._can_pass_restore = True
        self._can_scale_up = True
        self._can_scale_down = True
        self._can_restore = True
        self._ext_locked = False

    def from_busy_add_ps(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_add_pl(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_dead_ps(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_dead_pl(self):
        self.target_instance.logger_debug(str(self))

    def from_free(self):
        raise StrangeState()

    def from_memory_request(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()


class BusyAddPS(State):

    def __init__(self, target_instance):
        super(BusyAddPS, self).__init__(target_instance)
        self._can_pass_add = True
        self._can_pass_restore = True
        self._can_scale_up = False
        self._can_scale_down = False
        self._can_restore = True
        self._ext_locked = False

    def from_busy_add_ps(self):
        self.target_instance.logger_debug(str(self))
        self.target_instance.clear_last_add_message()

    def from_busy_add_pl(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_dead_ps(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()

    def from_busy_dead_pl(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()

    def from_free(self):
        self.target_instance.logger_debug(str(self))

    def from_memory_request(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()


class BusyAddPL(State):

    def __init__(self, target_instance):
        super(BusyAddPL, self).__init__(target_instance)
        self._can_pass_add = True
        self._can_pass_restore = True
        self._can_scale_up = False
        self._can_scale_down = False
        self._can_restore = True
        self._ext_locked = False

    def from_busy_add_ps(self):
        self.target_instance.logger_debug(str(self))
        self.target_instance.clear_last_add_message()

    def from_busy_add_pl(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_dead_ps(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()

    def from_busy_dead_pl(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()

    def from_free(self):
        self.target_instance.logger_debug(str(self))

    def from_memory_request(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()


class BusyDeadPL(State):

    def __init__(self, target_instance):
        super(BusyDeadPL, self).__init__(target_instance)
        self._can_pass_add = False       # This means that we cannot pass r_of_r requests
        self._can_pass_restore = True    # This means that we can pass r_of_r requests
        self._can_scale_up = False
        self._can_scale_down = False
        self._can_restore = False
        self._ext_locked = False

    def from_busy_add_ps(self):
        self.target_instance.logger_debug(str(self))
        self.target_instance.clear_last_add_message()

    def from_busy_add_pl(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_dead_ps(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_dead_pl(self):
        self.target_instance.logger_debug(str(self))

    def from_free(self):
        self.target_instance.logger_debug(str(self))

    def from_memory_request(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()


class BusyDeadPS(State):

    def __init__(self, target_instance):
        super(BusyDeadPS, self).__init__(target_instance)
        self._can_pass_add = False       # This means that we cannot pass r_of_r requests
        self._can_pass_restore = True    # This means that we can pass r_of_r requests
        self._can_scale_up = False
        self._can_scale_down = False
        self._can_restore = False
        self._ext_locked = False

    # This function is necessary if we are the originators of the DEAD message
    def flip_restore(self):
        self._can_restore = not self._can_restore

    def from_busy_add_ps(self):
        self.target_instance.logger_debug(str(self))
        self.target_instance.clear_last_add_message()

    def from_busy_add_pl(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_dead_ps(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_dead_pl(self):
        self.target_instance.logger_debug(str(self))

    def from_free(self):
        self.target_instance.logger_debug(str(self))

    def from_memory_request(self):
        self.target_instance.logger_debug(str(self))


class MemoryRequest(State):

    def __init__(self, target_instance):
        super(MemoryRequest, self).__init__(target_instance)
        self._can_pass_add = False       # This means that we cannot pass r_of_r requests
        self._can_pass_restore = False    # This means that we cannot pass r_of_r requests
        self._can_scale_up = False
        self._can_scale_down = False
        self._can_restore = False
        self._ext_locked = True

    # This function is necessary if we are the originators of the DEAD message
    def flip_restore(self):
        self._can_restore = not self._can_restore

    def from_busy_add_ps(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()

    def from_busy_add_pl(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()

    def from_busy_dead_ps(self):
        self.target_instance.logger_debug(str(self))

    def from_busy_dead_pl(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()

    def from_free(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()

    def from_memory_request(self):
        self.target_instance.logger_debug(str(self))
        raise StrangeState()


class TransitionTable(object):

    def __init__(self, transition_states, transition_table, start_state, target_instance):
        self.target_instance = target_instance
        self._transition_states = self._put_up_states(transition_states)
        self._transition_table = transition_table
        self._current_state = self._transition_states[start_state]
        print self._current_state

    def _put_up_states(self, string_states):
        list_states = {}
        i = 0
        for n in string_states:
            list_states[i] = eval(n)(self.target_instance)
            i += 1
        return list_states

    def get_current_state(self):
        return self._current_state

    def search_condition(self, condition_to_search):
            curr_name = self._current_state.__class__.__name__
            search_row = self._transition_table[curr_name]
            for x in xrange(len(search_row)):
                if search_row[x] is not None and search_row[x] == condition_to_search:
                        return self._transition_states[x]
            return None

    def change_state(self, condition):
        next_state = self.search_condition(condition)
        if next_state is not None:
            prev_state = self._current_state
            self._current_state = next_state
            self._current_state.transfer_from(prev_state)
        else:
            raise StrangeState()


class StrangeState(Exception):

    def __init__(self):
        self.message = "This is not a well-founded state transition!"


class Target(object):

    def __init__(self):
        self._my_attr = ''

    def get_my_attr(self):
        return "This is my attr " + str(self._my_attr)

    def set_my_attr(self, new_attr):
        self._my_attr = new_attr

if __name__ == "__name__":

    # dict_state = {0: "Free", 1: "BusyAddPS", 2: "BusyAddPL", 3: "BusyDeadPL", 4: "BusyDeadPS"}

    transition_table_param = {"Free": [None, "pas", "pal", "pdl", "pds", None],
                              "BusyAddPS": ["added_or_pa", "paa_and_ps", "paa_and_pl", "pad_and_pl", "pad_and_ps",
                                            None],
                              "BusyAddPL": ["added_or_pa", "paa_and_ps", "paa_and_pl", "pad_and_pl", "pad_and_ps",
                                            None],
                              "BusyDeadPL": ["restored_or_pa", None, None, "pad_and_pl", "pad_and_ps", None],
                              "BusyDeadPS": ["restored_or_pa", None, None, "pad_and_pl", "pad_and_ps", "m_started"],
                              "MemoryRequest": [None, None, None, None, None, "m_finished"]}

    states_param = ["Free", "BusyAddPS", "BusyAddPL", "BusyDeadPL", "BusyDeadPS"]
    # mapping_to_do = {"S1:S2": "pas", "S2:S3": "pal", "S3:S1": ""}
    new_target = Target()

    table_instance = TransitionTable(states_param, transition_table_param, 0, new_target)

    print new_target.get_my_attr()

    try:
        table_instance.change_state(condition="pas")
    except StrangeState as s:
        print s.message

    print new_target.get_my_attr()

    try:
        table_instance.change_state(condition="pad")
    except StrangeState as s:
        print s.message

    print new_target.get_my_attr()

    try:
        table_instance.change_state(condition="pad_and_pl")
    except StrangeState as s:
        print s.message

    print new_target.get_my_attr()

    try:
        table_instance.change_state(condition="restored_or_pa")
    except StrangeState as s:
        print s.message

    print new_target.get_my_attr()
