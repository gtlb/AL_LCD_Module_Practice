import configparser
import Constants.Constants as C
from Constants.Enums import Axis as AXIS
from Constants.Enums import Direction as DIR
from Constants.Enums import PinMap as PIN

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
      config = configparser.ConfigParser()
      config.read(C.CONFIG_FILEPATH)

      loadedPinSol = int(config.get('PinMap', 'Sol'))

      pinMapX = {}
      pinMapX[PIN.CLK] = int(config.get('PinMap', 'XClk'))
      pinMapX[PIN.DIR] = int(config.get('PinMap', 'XDir'))
      pinMapX[PIN.ENA] = int(config.get('PinMap', 'XEna'))

      pinMapY = {}
      pinMapY[PIN.CLK] = int(config.get('PinMap', 'YClk'))
      pinMapY[PIN.DIR] = int(config.get('PinMap', 'YDir'))
      pinMapY[PIN.ENA] = int(config.get('PinMap', 'YEna'))

      pinMapZ = {}
      pinMapZ[PIN.CLK] = int(config.get('PinMap', 'ZClk'))
      pinMapZ[PIN.DIR] = int(config.get('PinMap', 'ZDir'))
      pinMapZ[PIN.ENA] = int(config.get('PinMap', 'ZEna'))

      RunConfig.pinMap = {}
      RunConfig.pinMap[AXIS.X] = pinMapX
      RunConfig.pinMap[AXIS.Y] = pinMapY
      RunConfig.pinMap[AXIS.Z] = pinMapZ

      RunConfig.axisDelay = {}
      RunConfig.axisDelay[AXIS.X] = float(config.get('AxisDelay', 'X'))
      RunConfig.axisDelay[AXIS.Y] = float(config.get('AxisDelay', 'Y'))
      RunConfig.axisDelay[AXIS.Z] = float(config.get('AxisDelay', 'Z'))

      RunConfig.stepDirection = {}
      RunConfig.stepDirection[AXIS.X] = DIR.MINUS if config.get('StepDirection', 'X') == 'Minus' else DIR.PLUS
      RunConfig.stepDirection[AXIS.Y] = DIR.MINUS if config.get('StepDirection', 'Y') == 'Minus' else DIR.PLUS
      RunConfig.stepDirection[AXIS.Z] = DIR.MINUS if config.get('StepDirection', 'Z') == 'Minus' else DIR.PLUS

      RunConfig.pinSol = loadedPinSol

      print(RunConfig.pinSol)
      print(RunConfig.pinMap)
      print(RunConfig.axisDelay)
      print(RunConfig.stepDirection)

      RunConfig.__instance = self
