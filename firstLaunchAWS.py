# manually build and launch your instances
# remember that the ip field deals with a private ip


def _get_parameter(node_id, private_ip, min_key, max_key):
    p = {"id": node_id, "ip": private_ip, "min_key": min_key, "max_key": max_key}
    return p


def launchApplicationAWS(optionals):
    from CellCycle.AWS.AWSlib import startInstanceAWS
    from start import loadSettingsAndLogger

    # needed for aws launch
    settings, logger = loadSettingsAndLogger()

    # every instance has an element
    params_list = {}

    # default vpc (virtual private network) has a class of 172.31.0.0\16
    # so we can create private ip from 172.31.0.1 to 172.31.255.254
    # 172.31.1.0\8 is reserved
    # I suggest to use (just for initial nodes) 172.31.20.0\8
    # for example, create 3 nodes:
    # 172.31.20.1
    # 172.31.20.2
    # 172.31.20.3

    first = _get_parameter(node_id="1", private_ip="172.31.20.1", min_key="0", max_key="19")
    params_list["master_of_master"] = first

    second = _get_parameter(node_id="2", private_ip="172.31.20.2", min_key="20", max_key="39")
    params_list["master"] = second

    third = _get_parameter(node_id="3", private_ip="172.31.20.3", min_key="40", max_key="59")
    params_list["myself"] = third

    fourth = _get_parameter(node_id="4", private_ip="172.31.20.4", min_key="60", max_key="79")
    params_list["slave"] = fourth

    fifth = _get_parameter(node_id="5", private_ip="172.31.20.5", min_key="80", max_key="99")
    params_list["slave_of_slave"] = fifth

    # only debug
    # from CellCycle.ChainModule.Generator import Generator
    # from json import dumps,loads
    # generator = Generator(logger=logger, settings=settings, json_arg=loads(dumps(params_list)))
    # generator.create_process_environment()

    # launch
    for ins in params_list:
        startInstanceAWS(settings, logger, ins, ins["ip"])

if __name__ == "__main__":
    import sys
    launchApplicationAWS(sys.argv[1:])
