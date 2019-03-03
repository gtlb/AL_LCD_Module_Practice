import configparser
import Constants.Constants as C
from Models.RunConfig import RunConfig as RC
from Constants.Enums import Axis as AXIS
from Constants.Enums import Direction as DIR
from Constants.Enums import PinMap as PIN

def LoadRunConfig():
    config = configparser.ConfigParser()
    config.read(C.CONFIG_FILEPATH)

    pinSol = int(config.get('PinMap', 'Sol'))

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

    pinMap = {}
    pinMap[AXIS.X] = pinMapX
    pinMap[AXIS.Y] = pinMapY
    pinMap[AXIS.Z] = pinMapZ

    axisDelay = {}
    axisDelay[AXIS.X] = float(config.get('AxisDelay', 'X'))
    axisDelay[AXIS.Y] = float(config.get('AxisDelay', 'Y'))
    axisDelay[AXIS.Z] = float(config.get('AxisDelay', 'Z'))

    stepDirection = {}
    stepDirection[AXIS.X] = DIR.MINUS if config.get('StepDirection', 'X') == 'Minus' else DIR.PLUS
    stepDirection[AXIS.Y] = DIR.MINUS if config.get('StepDirection', 'Y') == 'Minus' else DIR.PLUS
    stepDirection[AXIS.Z] = DIR.MINUS if config.get('StepDirection', 'Z') == 'Minus' else DIR.PLUS

    runConfig = RC.getInstance()

    runConfig.pinSol = pinSol
    runConfig.pinMap = pinMap
    runConfig.axisDelay = axisDelay
    runConfig.stepDirection = stepDirection

    print(pinSol)
    print(pinMap)
    print(axisDelay)
    print(stepDirection)
