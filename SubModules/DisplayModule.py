import Header as H
import Constants.Constants as C
from Constants.Enums import PinMap as PIN
from Models.RunConfig import RunConfig as RC
from Constants.Enums import PwmConfig as PWM

RunConfig = RC.getInstance()
port = None

#### Main Funcitons ############################################################

# Setup LCD Module
def Setup():
  import serial

  # Initialize the serial IO, clear the screen, and turn the blinker off.
  port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=3.0)
  port.write('$C\r'.encode())
  port.write('$B,0\r'.encode())

# Display Text to the Raspberry Pi LCD Screen.
def DisplayTexts(displayTexts):
  for i in range(C.LCD_LEN):
    displayText = displayTexts[i] + " " * (20 - len(displayText))

    port.write(('$G,{},1\r'.format(str(i%4+1))).encode())
    port.write(('$T,{}\r'.format(displayText)).encode())

################################################################################

#### Helper Functions ##########################################################

def FormatTemp(temp):
  return "N/A" if temp is None else "{0:0.2f}C".format(temp)

################################################################################

def DisplayJogAxis(axis):
  return [
    "JOG {}".format(axis),
    " ",
    "^ : Up Arrow",
    "v : Down Arrow"
  ]

#### Display Functions #########################################################

def DisplayPWM(RTDTemp):
  return [
    "PWM      {}".format(FormatTemp(RTDTemp)),
    " ",
    "{} Hz".format(RunConfig.pwm[PWM.FREQUENCY]),
    "{} %".format(RunConfig.pwm[PWM.DUTY_CYCLE])
  ]

def DisplayPWMSequence(RTDTemp, pwmSequenceIndex):
  # TODO: Enum this
  [targetTemp, targetDir, level] = RunConfig.pwmSequence["Sequence"][pwmSequenceIndex]

  return [
    "PWM Seq.  {}".format(FormatTemp(RTDTemp)),
    " ",
    "Target Temp: {}, Dir: {}".format(targetTemp, targetDir),
    "PWM Level: {}".format(level)
  ]

def DisplayPWMMatrix(RTDTemp, PWMMatrixCurrentCondition):
  [observedTemp, observedSlope, level] = PWMMatrixCurrentCondition

  return [
    "PWM Mat.  {}".format(FormatTemp(RTDTemp)),
    " ",
    "Temp: {}, Slope: {}".format(observedTemp, observedSlope),
    "PWM Level: {}".format(level)
  ]

def DisplayPWMFrequency():
  return [
    "PWM Frequency",
    "{} Hz".format(RunConfig.pwm[PWM.FREQUENCY]),
    "^ : Up Arrow",
    "v : Down Arrow"
  ]

def DisplayPWMDutyCycle():
  return [
    "PWM Duty Cycle",
    "{} %".format(RunConfig.pwm[PWM.DUTY_CYCLE]),
    "^ : Up Arrow",
    "v : Down Arrow"
  ]

def DisplayPinMapSingle(pin):
  pinMap = RunConfig.pinMap
  displayTexts = ["PIN {}".format(pin), " ", " ", " "]

  if pin in pinMap.keys():
    displayTexts[1] = "{}: {}".format(PIN.CLK, pinMap[pin][PIN.CLK])
    displayTexts[2] = "{}: {}".format(PIN.DIR, pinMap[pin][PIN.DIR])
    displayTexts[3] = "{}: {}".format(PIN.ENA, pinMap[pin][PIN.ENA])

  return displayTexts

def DisplayEntries(displayList, pdi, ci):
  displayTexts = []

  for i in range(C.LCD_LEN):
    if pdi + i < len(displayList):
      if i == ci:
        displayTexts.append("> {}".format(displayList[pdi + i]))
      else:
        displayTexts.append("  {}".format(displayList[pdi + i]))
    else:
      displayTexts.append("  ")

  return displayTexts

################################################################################
