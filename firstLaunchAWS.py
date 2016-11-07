# manually build and launch your instances
# remember that the ip field deals with a private ip


def _get_parameter(node_id, private_ip, min_key, max_key):
    p = {"id": node_id, "ip": private_ip, "min_key": min_key, "max_key": max_key}
    return p


def create_instances_parameters():

    first = _get_parameter(node_id="1", private_ip="172.31.20.1", min_key="0", max_key="19")
    # parameter["master_of_master"] = first

    second = _get_parameter(node_id="2", private_ip="172.31.20.2", min_key="20", max_key="39")
    # parameter["master"] = second

    third = _get_parameter(node_id="3", private_ip="172.31.20.3", min_key="40", max_key="59")
    # parameter["myself"] = third

    fourth = _get_parameter(node_id="4", private_ip="172.31.20.4", min_key="60", max_key="79")
    # parameter["slave"] = fourth

    fifth = _get_parameter(node_id="5", private_ip="172.31.20.5", min_key="80", max_key="99")
    # parameter["slave_of_slave"] = fifth

    list_parameters = [first, second, third, fourth, fifth]

    list_len = len(list_parameters)

    result = []

    for l in xrange(list_len):
        parameter = {"master_of_master": list_parameters[l % list_len],
                     "master": list_parameters[(l + 1) % list_len],
                     "myself": list_parameters[(l + 2) % list_len],
                     "slave": list_parameters[(l + 3) % list_len],
                     "slave_of_slave": list_parameters[(l + 4) % list_len]}
        # print '-------------------'
        # print list_parameters[l % list_len]['id']
        # print list_parameters[(l+1) % list_len]['id']
        # print list_parameters[(l+2) % list_len]['id']
        # print list_parameters[(l+3) % list_len]['id']
        # print list_parameters[(l+4) % list_len]['id']
        # print '-------------------'
        # print '-------------------'

        # for k, v in parameter.iteritems():
        #     print "{}, {}".format(k, v)

        # print '-------------------'

        result.append(parameter)

    return result


def launchApplicationAWS(optionals):
    from CellCycle.AWS.AWSlib import startInstanceAWS
    from start import loadSettingsAndLogger

    # needed for aws launch
    currentProfile = {}
    currentProfile["profile_name"] = optionals[0]
    currentProfile["key_pair"] = optionals[1]
    settings, logger = loadSettingsAndLogger(currentProfile)

    # every instance has an element
    params_list = create_instances_parameters()

    # default vpc (virtual private network) has a class of 172.31.0.0\16
    # so we can create private ip from 172.31.0.1 to 172.31.255.254
    # 172.31.1.0\8 is reserved
    # I suggest to use (just for initial nodes) 172.31.20.0\8
    # for example, create 3 nodes:
    # 172.31.20.1
    # 172.31.20.2
    # 172.31.20.3

    # only debug
    # from CellCycle.ChainModule.Generator import Generator
    # from json import dumps,loads
    # generator = Generator(logger=logger, settings=settings, json_arg=loads(dumps(params_list)))
    # generator.create_process_environment()

    # for ins in params_list:
    #     print "######## NEW NODE #######"
    #     for k, v in ins.iteritems():
    #         print "{}, {}".format(k, v)
    #     print "#########################"

    # launch
    for ins in params_list:
        startInstanceAWS(settings, logger, ins, ins["myself"]["ip"])

if __name__ == "__main__":
    import sys
    launchApplicationAWS(sys.argv[1:])
