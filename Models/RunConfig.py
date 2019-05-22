import ast
import configparser
import json
import Constants.Constants as C
from os import listdir
from pynput.keyboard import Key
from Constants.Enums import Axis as AXIS
from Constants.Enums import Direction as DIR
from Constants.Enums import PinMap as PIN
from Constants.Enums import PwmConfig as PWM

class RunConfig:
  __instance = None

  pinSol = None
  pinMap = None
  axisDelay = None
  stepDirection = None
  pwm = None
  pwmSequence = None
  pwmMatrix = None
  runSequencesTitles = None

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

      RunConfig.pwm = {}
      RunConfig.pwm[PWM.ON_OFF_PIN] = int(config.get('PWM', PWM.ON_OFF_PIN))
      RunConfig.pwm[PWM.PWM_PIN] = int(config.get('PWM', PWM.PWM_PIN))
      RunConfig.pwm[PWM.FREQUENCY] = int(config.get('PWM', PWM.FREQUENCY))
      RunConfig.pwm[PWM.DUTY_CYCLE] = int(config.get('PWM', PWM.DUTY_CYCLE))
      RunConfig.pwm[PWM.FREQUENCY_LIST] \
        = ast.literal_eval(config.get('PWM', PWM.FREQUENCY_LIST))
      RunConfig.pwm[PWM.DUTY_CYCLE_LIST] \
        = ast.literal_eval(config.get('PWM', PWM.DUTY_CYCLE_LIST))

      fp = open(C.PWM_SEQUENCE_FILEPATH)
      RunConfig.pwmSequence = json.load(fp)

      fp = open(C.PWM_MATRIX_FILEPATH)
      RunConfig.pwmMatrix = json.load(fp)

      RunConfig.runSequencesTitles = listdir(C.RUN_SEQUENCES_FILEPATH)

      print(RunConfig.pinSol)
      print(RunConfig.pinMap)
      print(RunConfig.axisDelay)
      print(RunConfig.stepDirection)
      print(RunConfig.pwm)
      print(RunConfig.pwmSequence)
      print(RunConfig.pwmMatrix)
      print(RunConfig.runSequencesTitles)

      RunConfig.__instance = self


  def ModifyPWMFrequency(self, key):
    freqList = RunConfig.pwm[PWM.FREQUENCY_LIST]
    index = freqList.index(RunConfig.pwm[PWM.FREQUENCY])
    if key is Key.up and index+1 < len(freqList):
      RunConfig.pwm[PWM.FREQUENCY] = freqList[index+1]
    elif key is Key.down and index > 0:
      RunConfig.pwm[PWM.FREQUENCY] = freqList[index-1]


  def ModifyPWMDutyCycle(self, key):
    dcList = RunConfig.pwm[PWM.DUTY_CYCLE_LIST]
    index = dcList.index(RunConfig.pwm[PWM.DUTY_CYCLE])
    if key is Key.up and index+1 < len(dcList):
      RunConfig.pwm[PWM.DUTY_CYCLE] = dcList[index+1]
    elif key is Key.down and index > 0:
      RunConfig.pwm[PWM.DUTY_CYCLE] = dcList[index-1]
