# manually build and launch your instances
def launchApplicationAWS(optionals):
    from CellCycle.AWS.AWSlib import startInstanceAWS
    from start import loadSettingsAndLogger

    # needed for aws launch
    settings, logger = loadSettingsAndLogger()

    # every instance has an element
    paramsList = []

    first = {}
    first["prova1"] = "ciao"
    first["prova2"] = "superciao"
    paramsList.append(first)

    second = {}
    second["indirizzo"] = "ciao"
    second["home"] = "ciaone"
    paramsList.append(second)

    third = {}
    third["indirizzo"] = "ibaffidicantone"
    third["home"] = "cantone"
    paramsList.append(third)

    fourth = {}
    fourth["indirizzo"] = "davide"
    fourth["home"] = "ci puoi guardare le borse"
    paramsList.append(fourth)

    #launch
    for ins in paramsList:
        startInstanceAWS(settings, logger, ins)

if __name__ == "__main__":
    import sys
    launchApplicationAWS(sys.argv[1:])
