from Constants.Enums import Axis as AXIS

class TeachingPoints:
    __instance = None

    # Dictionary containing teaching points.
    teachingPoints = None

    @staticmethod
    def getInstance():
        if TeachingPoints.__instance == None:
            TeachingPoints()
        return TeachingPoints.__instance

    def __init__(self):
        if TeachingPoints.__instance != None:
            raise Exception("Initialize called on an initialized singleton.")
        else:
            TeachingPoints.__instance = self
