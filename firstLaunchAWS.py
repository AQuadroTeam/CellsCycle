# manually build and launch your instances
def launchApplicationAWS(optionals):
    from CellCycle.AWS.AWSlib import startInstanceAWS
    from start import loadSettingsAndLogger

    # needed for aws launch
    currentProfile = {}
    currentProfile["profile_name"]  = optionals[0]
    currentProfile["key_pair"]  = optionals[1]
    settings, logger = loadSettingsAndLogger(currentProfile)

    # every instance has an element
    paramsList = []

    # default vpc (virtual private network) has a class of 172.31.0.0\16
    # so we can create private ip from 172.31.0.1 to 172.31.255.254
    # 172.31.1.0\8 is reserved
    # I suggest to use (just for initial nodes) 172.31.20.0\8
    # for example, create 3 nodes:
    # 172.31.20.1
    # 172.31.20.2
    # 172.31.20.3

    first = {}
    first["prova1"] = "ciao"
    first["prova2"] = "superciao"
    first["privateIp"] = "172.31.20.1"
    paramsList.append(first)

    second = {}
    second["indirizzo"] = "ciao"
    second["home"] = "ciaone"
    second["privateIp"] = "172.31.20.2"
    paramsList.append(second)

    third = {}
    third["indirizzo"] = "ibaffidicantone"
    third["home"] = "cantone"
    third["privateIp"] = "172.31.20.3"
    paramsList.append(third)

    fourth = {}
    fourth["indirizzo"] = "davide"
    fourth["home"] = "ci puoi guardare le borse"
    fourth["privateIp"] = "172.31.20.4"
    paramsList.append(fourth)

    #launch
    for ins in paramsList:
        startInstanceAWS(settings, logger, ins, ins["privateIp"])

if __name__ == "__main__":
    import sys
    launchApplicationAWS(sys.argv[1:])
