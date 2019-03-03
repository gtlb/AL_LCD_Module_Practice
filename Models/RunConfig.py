class RunConfig:
    __instance = None

    pinSol = None
    pinMap = None
    axisDelay = None
    stepDirection = None

    @staticmethod
    def getInstance():
        if RunConfig.__instance == None:
            RunConfig()
        return RunConfig.__instance

    def __init__(self):
        if RunConfig.__instance != None:
            raise Exception("Initialize called on an initialized singleton.")
        else:
            RunConfig.__instance = self
