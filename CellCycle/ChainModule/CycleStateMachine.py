class State(object):

    def __init__(self, target_instance):
        self.target_instance = target_instance
        self.transitions = {"Free": self.from_free,
                            "BusyAddPS": self.from_busy_add_ps,
                            "BusyAddPL": self.from_busy_add_pl,
                            "BusyDeadPS": self.from_busy_dead_ps,
                            "BusyDeadPL": self.from_busy_dead_pl}

    def __str__(self):
        return "I am a state {}".format(self.__class__.__name__)

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


class Free(State):

    def __init__(self, target_instance):
        super(Free, self).__init__(target_instance)

    def from_busy_add_ps(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_add_pl(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_dead_ps(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_dead_pl(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_free(self):
        raise StrangeState()


class BusyAddPS(State):

    def __init__(self, target_instance):
        super(BusyAddPS, self).__init__(target_instance)

    def from_busy_add_ps(self):
        raise StrangeState()

    def from_busy_add_pl(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_dead_ps(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_dead_pl(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_free(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))


class BusyAddPL(State):

    def __init__(self, target_instance):
        super(BusyAddPL, self).__init__(target_instance)

    def from_busy_add_ps(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_add_pl(self):
        raise StrangeState()

    def from_busy_dead_ps(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_dead_pl(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_free(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))


class BusyDeadPL(State):

    def __init__(self, target_instance):
        super(BusyDeadPL, self).__init__(target_instance)

    def from_busy_add_ps(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_add_pl(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_dead_ps(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_dead_pl(self):
        raise StrangeState()

    def from_free(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))


class BusyDeadPS(State):

    def __init__(self, target_instance):
        super(BusyDeadPS, self).__init__(target_instance)

    def from_busy_add_ps(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_add_pl(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_busy_dead_ps(self):
        raise StrangeState()

    def from_busy_dead_pl(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))

    def from_free(self):
        print str(self)
        self.target_instance.set_my_attr(str(self))


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

    transition_table_param = {"Free": [None, "pas", "pal", "pdl", "pds"],
                              "BusyAddPS": ["added_or_pa", None, "paa_and_pl", "pad_and_pl", "pad_and_ps"],
                              "BusyAddPL": ["added_or_pa", "paa_and_ps", None, "pad_and_pl", "pad_and_ps"],
                              "BusyDeadPL": ["restored_or_pa", None, None, None, "pad_and_ps"],
                              "BusyDeadPS": ["restored_or_pa", None, None, "pad_and_pl", None]}

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

