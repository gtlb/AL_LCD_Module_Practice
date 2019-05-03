import Header as H
import threading
import time
import Jog
import PWMHandler
import Constants.Constants as C
import DisplayLCD as LCD
import Utilities.FileHandler as FH
from Models.RunConfig import RunConfig as RC
from threading import Lock
from pynput.keyboard import Key, Listener, Controller
from Constants.Enums import Axis as AXIS
from Constants.Enums import IO
from Constants.Enums import PageStyle as PAGE_STYLE
from Constants.Enums import Direction as DIR
from Constants.Enums import STATE

DISPLAY = "DISPLAY"
VALUE = "VALUE"
MODE = "MODE"

RTD = None
RTDTemp = None

RunConfig = RC.getInstance()

currentState = STATE.MAIN

# This code will only get executed for Raspberry Pi.
if H.__raspberry__ :
  import RaspberrySetup as RS
  import SubModules.RTDModule

  RS.Setup()

  LCD.Setup()

  RTD = RTDModule.Setup()

def enum(**enums):
  return type('Enum', (), enums)

states = [
  STATE.MAIN,
  STATE.JOG,
  STATE.JOG_AXIS,
  STATE.PWM,
  STATE.PWM_SEQUENCE,
  STATE.PWM_MATRIX,
  STATE.SETTINGS,
  STATE.PINMAP,
  STATE.PINMAP_SINGLE,
  STATE.PWM_FREQUENCY,
  STATE.PWM_DUTY_CYCLE
]

# This data structure represents the state machine on how the program runs.
stateMachine = {}
# This index shows wich index in LCD the cursor should be displayed.
cursorIndex = {}
# This index shows from which index, the page should be displayed.
pageDisplayIndex = {}
# This setting defines how a page should be displayed and interacted.
pageSettings = {}

for state in states:
  cursorIndex[state] = 0
  pageDisplayIndex[state] = 0

  if state is STATE.MAIN:
    stateMachine[state] = {
      DISPLAY   : [C.JOG, C.PWM, C.PWM_SEQUENCE, C.PWM_MATRIX, C.SETTINGS],
      Key.right : [STATE.JOG, STATE.PWM, STATE.PWM_SEQUENCE, STATE.PWM_MATRIX,
                   STATE.SETTINGS]
    }
    pageSettings[state] = { MODE: PAGE_STYLE.NAVIGATION }
  elif state is STATE.JOG:
    stateMachine[state] = {
      DISPLAY   : [AXIS.X, AXIS.Y, AXIS.Z],
      VALUE     : [AXIS.X, AXIS.Y, AXIS.Z],
      Key.left  : STATE.MAIN,
      Key.right : [STATE.JOG_AXIS, STATE.JOG_AXIS, STATE.JOG_AXIS]
    }
    pageSettings[state] = { MODE: PAGE_STYLE.NAVIGATION }
  elif state is STATE.JOG_AXIS:
    stateMachine[state] = { Key.left  : STATE.JOG }
    pageSettings[state] = { MODE: PAGE_STYLE.JOG }
  elif state is STATE.PWM:
    stateMachine[state] = { Key.left  : STATE.MAIN }
    pageSettings[state] = { MODE: PAGE_STYLE.PWM }
  elif state is STATE.PWM_SEQUENCE:
    stateMachine[state] = { Key.left  : STATE.MAIN }
    pageSettings[state] = { MODE: PAGE_STYLE.PWM_SEQUENCE }
  elif state is STATE.PWM_MATRIX:
    stateMachine[state] = { Key.left  : STATE.MAIN }
    pageSettings[state] = { MODE: PAGE_STYLE.PWM_MATRIX }
  elif state is STATE.SETTINGS:
    stateMachine[state] = {
      DISPLAY   : [C.PINMAP, C.PWM_FREQUENCY, C.PWM_DUTY_CYCLE],
      Key.left  : STATE.MAIN,
      Key.right : [STATE.PINMAP, STATE.PWM_FREQUENCY, STATE.PWM_DUTY_CYCLE]
    }
    pageSettings[state] = { MODE: PAGE_STYLE.NAVIGATION }
  elif state is STATE.PINMAP:
    stateMachine[state] = {
      DISPLAY   : [AXIS.X, AXIS.Y, AXIS.Z, IO.VALVE],
      VALUE     : [AXIS.X, AXIS.Y, AXIS.Z, IO.VALVE],
      Key.left  : STATE.SETTINGS,
      Key.right : [STATE.PINMAP_SINGLE, STATE.PINMAP_SINGLE, STATE.PINMAP_SINGLE,
                   STATE.PINMAP_SINGLE]
    }
    pageSettings[state] = { MODE: PAGE_STYLE.NAVIGATION }
  elif state is STATE.PINMAP_SINGLE:
    stateMachine[state] = { Key.left  : STATE.PINMAP }
    pageSettings[state] = { MODE: PAGE_STYLE.EDIT }
  elif state is STATE.PWM_FREQUENCY:
    stateMachine[state] = { Key.left  : STATE.SETTINGS }
    pageSettings[state] = { MODE: PAGE_STYLE.EDIT }
  elif state is STATE.PWM_DUTY_CYCLE:
    stateMachine[state] = { Key.left  : STATE.SETTINGS }
    pageSettings[state] = { MODE: PAGE_STYLE.EDIT }
  else:
    raise Exception("Unsupported state has been encountered (State Machine).")


stateMachineLen = len(stateMachine)
cursorIndexLen = len(cursorIndex)
pageDisplayIndexLen = len(pageDisplayIndex)
pageSettingsLen = len(pageSettings)

# This check confirms all settings have been set properly until here.
if (stateMachineLen != cursorIndexLen
    or cursorIndexLen != pageDisplayIndexLen
    or pageDisplayIndexLen != pageSettingsLen):
  print("stateMachine Len: " + str(len(stateMachine)))
  print("cursorIndex Len: " + str(len(cursorIndex)))
  print("pageDisplayIndex Len: " + str(len(pageDisplayIndex)))
  print("pageSettings Len: " + str(len(pageSettings)))
  raise Exception("Some settings might be wrong."
                + "Please check your preset data structs.")


def on_press(key):
  if H.__verbose__:
    print('{0} pressed'.format(key))

  pageMode = pageSettings[currentState][MODE]

  # UP and DOWN case
  if key in [Key.up, Key.down]:

    if pageMode is PAGE_STYLE.JOG:
      jogIndex = cursorIndex[STATE.JOG] + pageDisplayIndex[STATE.JOG]
      axis = stateMachine[STATE.JOG][VALUE][jogIndex]

      jogMesage = ", Plus" if key is Key.up else ", Minus"

      if H.__verbose__:
        print("Jogging Axis " + str(axis) + jogMesage)

      direction = DIR.PLUS if key is Key.up else DIR.MINUS
      Jog.StartJog(axis, direction)

    if pageMode is PAGE_STYLE.EDIT:
      if currentState is STATE.PWM_FREQUENCY:
        RunConfig.ModifyPWMFrequency(key)
      elif currentState is STATE.PWM_DUTY_CYCLE:
        RunConfig.ModifyPWMDutyCycle(key)

    if pageMode is PAGE_STYLE.PWM:
      RunConfig.ModifyPWMDutyCycle(key)
      PWMHandler.UpdateDutyCycle()

  if key is Key.left and Key.left in stateMachine[currentState].keys():
    if currentState in [STATE.PWM, STATE.PWM_SEQUENCE, STATE.PWM_MATRIX]:
      PWMHandler.StopPWM()

  if key is Key.right and Key.right in stateMachine[currentState].keys():
    absoluteIndex = pageDisplayIndex[currentState] + cursorIndex[currentState]
    if absoluteIndex < len(stateMachine[currentState][key]):
      if stateMachine[currentState][key][absoluteIndex] is STATE.PWM:
        PWMHandler.StartPWM(RTD)
      elif stateMachine[currentState][key][absoluteIndex] is STATE.PWM_SEQUENCE:
        PWMHandler.StartPWMSequence(RTD)
      elif stateMachine[currentState][key][absoluteIndex] is STATE.PWM_MATRIX:
        PWMHandler.StartPWMMatrix(RTD)


def on_release(key):
  global currentState
  if H.__verbose__:
    print('{0} release'.format(key))

  pageMode = pageSettings[currentState][MODE]

  # UP and DOWN case
  if key in [Key.up, Key.down]:
    if pageMode is PAGE_STYLE.NAVIGATION:
      moveCursorUpDown(currentState, key)

    if pageMode is PAGE_STYLE.JOG:
      if H.__verbose__:
        print("Stop Jogging")

      Jog.StopJog()

    if pageMode is PAGE_STYLE.EDIT:
      # TODO: Not yet implemented. Up and down change values.
      pass

  # LEFT and RIGHT case (navigation)
  if key is Key.left and Key.left in stateMachine[currentState].keys():
    currentState = stateMachine[currentState][key]

  if key is Key.right and Key.right in stateMachine[currentState].keys():
    absoluteIndex = pageDisplayIndex[currentState] + cursorIndex[currentState]

    if absoluteIndex < len(stateMachine[currentState][key]):
      currentState = stateMachine[currentState][key][absoluteIndex]

  if key == Key.esc:
    # Stop listener
    return False

  DisplayLCD()

def moveCursorUpDown(state, direction):
  global cursorIndex, pageDisplayIndex

  maxLength = len(stateMachine[state][DISPLAY]) \
              if DISPLAY in stateMachine[state] else 0

  if direction == Key.up:
    # You are at the top of the page, do nothing.
    if cursorIndex[state] == 0 and pageDisplayIndex[state] == 0:
      # do nothing
      pass
    # Your cursor is at the top, but not at the top of the page.
    elif cursorIndex[state] == 0:
      pageDisplayIndex[state] -= 1
    # Your cursor is not at the top.
    else:
      cursorIndex[state] -= 1

  elif direction == Key.down:
    # You are at the bottom of the page, do nothing.
    if cursorIndex[state] + pageDisplayIndex[state] == maxLength-1:
      # do nothing
      pass
    # Your cursor is at the bottom, but not at the bottom of the page.
    elif cursorIndex[state] == C.LCD_LEN-1:
        pageDisplayIndex[state] += 1
    # Your cursor is not at the bottom.
    else:
      cursorIndex[state] += 1

def DisplayLCD():
  state = stateMachine[currentState]
  displayList = state[DISPLAY] if DISPLAY in state else []
  displayTexts = []

  # Get a list of strings to display.
  if currentState == STATE.JOG_AXIS:
    jogIndex = cursorIndex[STATE.JOG] + pageDisplayIndex[STATE.JOG]
    axis = stateMachine[STATE.JOG][VALUE][jogIndex]
    displayTexts = LCD.DisplayJogAxis(axis)

  elif currentState == STATE.PWM:
    displayTexts = LCD.DisplayPWM(PWMHandler.GetRTDTemp())

  elif currentState == STATE.PWM_SEQUENCE:
    displayTexts = LCD.DisplayPWMSequence(PWMHandler.GetRTDTemp(),
                     PWMHandler.GetPWMSequenceIndex())

  elif currentState == STATE.PWM_MATRIX:
    displayTexts = LCD.DisplayPWMMatrix(PWMHandler.GetRTDTemp(),
                     PWMHandler.GetPwmMatrixCurrentCondition())

  elif currentState == STATE.PWM_FREQUENCY:
    displayTexts = LCD.DisplayPWMFrequency()

  elif currentState == STATE.PWM_DUTY_CYCLE:
    displayTexts = LCD.DisplayPWMDutyCycle()

  elif currentState == STATE.PINMAP_SINGLE:
    pinIndex = cursorIndex[STATE.PINMAP] + pageDisplayIndex[STATE.PINMAP]
    pin = stateMachine[STATE.PINMAP][VALUE][pinIndex]
    displayTexts = LCD.DisplayPinMapSingle(pin)

  # This is the default case with multiple entries.
  else:
    ci = cursorIndex[currentState]
    pdi = pageDisplayIndex[currentState]
    displayTexts = LCD.DisplayEntries(displayList, pdi, ci)

  if H.__raspberry__ :
    LCD.DisplayTexts(displayTexts)

  if H.__verbose__ or not H.__raspberry__:
    print("--------------------")
    for i in range(C.LCD_LEN):
      print(displayTexts[i])
    print("--------------------")


if H.__verbose__:
  print("Key Listener Started")

keyListener = Listener(on_press=on_press, on_release=on_release)
keyListener.daemon = True
keyListener.start()

try:
  import datetime
  while(1):
    if currentState in [STATE.PWM, STATE.PWM_SEQUENCE, STATE.PWM_MATRIX]:
      DisplayLCD()

    time.sleep(1)
except KeyboardInterrupt:
  if H.__raspberry__ :
    RS.cleanup()
  print("Program terminated")
  pass
