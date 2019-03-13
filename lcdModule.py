import threading
import time
import DisplayLCD as LCD
import Utilities.FileHandler as FH
from Models.RunConfig import RunConfig as RC
from threading import Lock
from pynput.keyboard import Key, Listener, Controller
from Constants.Enums import Axis as AXIS
from Constants.Enums import IO as IO
from Constants.Enums import PageStyle as PAGE_STYLE
from Constants.Enums import Direction as DIR

__verbose__   = False
__raspberry__ = True

FH.LoadRunConfig()
RunConfig = RC.getInstance()

import Jog

if __raspberry__ :
  import RaspberrySetup as RS
  RS.Setup()
  
  import serial

  port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=3.0)

  port.write('$C\r'.encode())
  port.write('$B,0\r'.encode())


def enum(**enums):
  return type('Enum', (), enums)

arrowKeys = [Key.right, Key.left, Key.up, Key.down]

DISPLAY = "DISPLAY"
VALUE = "VALUE"
JOG = "JOG"
SETTINGS = "SETTINGS"
PINMAP = "PinMap"
MODE = "MODE"
LCD_LEN = 4

STATE = enum(
  MAIN        = "MAIN",
  JOG         = "JOG",
  JOG_AXIS    = "JOG_AXIS",
  SETTINGS    = "SETTINGS",
  PINMAP      = "PINMAP",
  PINMAP_SINGLE = "PINMAP_SINGLE"
)

AXIS_NAME = enum(
  X = "X",
  Y = "Y",
  Z = "Z",
  A = "A",
  B = "B"
)

stateMachine = {
  STATE.MAIN : {
    DISPLAY   : [JOG, SETTINGS, "Main Item 3", "Main Item 4",
               "Main Item 5", "Main Item 6"],
    Key.right : [STATE.JOG, STATE.SETTINGS]
  },
  STATE.JOG : {
    DISPLAY   : [AXIS_NAME.X, AXIS_NAME.Y, AXIS_NAME.Z],
    VALUE     : [AXIS.X, AXIS.Y, AXIS.Z],
    Key.left  : STATE.MAIN,
    Key.right : [STATE.JOG_AXIS, STATE.JOG_AXIS, STATE.JOG_AXIS]
  },
  STATE.JOG_AXIS : {
    DISPLAY   : [],
    Key.left  : STATE.JOG
  },

  STATE.SETTINGS : {
    DISPLAY   : [PINMAP],
    Key.left  : STATE.MAIN,
    Key.right : [STATE.PINMAP]
  },
  STATE.PINMAP : {
    DISPLAY   : [AXIS_NAME.X, AXIS_NAME.Y, AXIS_NAME.Z, IO.VALVE],
    VALUE     : [AXIS.X, AXIS.Y, AXIS.Z, IO.VALVE],
    Key.left  : STATE.SETTINGS,
    Key.right : [STATE.PINMAP_SINGLE, STATE.PINMAP_SINGLE, STATE.PINMAP_SINGLE,
                 STATE.PINMAP_SINGLE]
  },

  STATE.PINMAP_SINGLE : {
    DISPLAY  : [],
    Key.left : STATE.PINMAP
  }
}

currentState = STATE.MAIN
cursorIndex = {
  STATE.MAIN          : 0,
  STATE.JOG           : 0,
  STATE.JOG_AXIS      : 0,

  STATE.SETTINGS      : 0,
  STATE.PINMAP        : 0,
  STATE.PINMAP_SINGLE : 0
}

# This index shows from which index, the page should be displayed.
pageDisplayIndex = {
  STATE.MAIN          : 0,
  STATE.JOG           : 0,
  STATE.JOG_AXIS      : 0,

  STATE.SETTINGS      : 0,
  STATE.PINMAP        : 0,
  STATE.PINMAP_SINGLE : 0
}

# This setting defines how a page should be displayed and interacted.
pageSettings = {
  STATE.MAIN          : { MODE: PAGE_STYLE.NAVIGATION },
  STATE.JOG           : { MODE: PAGE_STYLE.NAVIGATION },
  STATE.JOG_AXIS      : { MODE: PAGE_STYLE.JOG },

  STATE.SETTINGS      : { MODE: PAGE_STYLE.NAVIGATION },
  STATE.PINMAP        : { MODE: PAGE_STYLE.NAVIGATION },
  STATE.PINMAP_SINGLE : { MODE: PAGE_STYLE.EDIT }
}


stateMachineLen = len(stateMachine)
cursorIndexLen = len(cursorIndex)
pageDisplayIndexLen = len(pageDisplayIndex)
pageSettingsLen = len(pageSettings)

if (stateMachineLen != cursorIndexLen
    or cursorIndexLen != pageDisplayIndexLen
    or pageDisplayIndexLen != pageSettingsLen):
  print("stateMachine Len: " + str(len(stateMachine)))
  print("cursorIndex Len: " + str(len(cursorIndex)))
  print("pageDisplayIndex Len: " + str(len(pageDisplayIndex)))
  print("pageSettings Len: " + str(len(pageSettings)))
  print("Some settings might be wrong. Please check your preset data structs.")

def StartKeyListener():
  print("Key Listener Started")
  keyListener = Listener(on_press=on_press, on_release=on_release)
  keyListener.daemon = True
  keyListener.start()

def on_press(key):
  if __verbose__:
    print('{0} pressed'.format(key))

  pageMode = pageSettings[currentState][MODE]

  # UP and DOWN case
  if key in [Key.up, Key.down]:

    if pageMode is PAGE_STYLE.JOG:
      jogIndex = cursorIndex[STATE.JOG] + pageDisplayIndex[STATE.JOG]
      axis = stateMachine[STATE.JOG][VALUE][jogIndex]

      jogMesage = ", Plus" if key is Key.up else ", Minus"

      if __verbose__:
        print("Jogging Axis " + str(axis) + jogMesage)

      direction = DIR.PLUS if key is Key.up else DIR.MINUS
      Jog.StartJog(axis, direction)


def on_release(key):
  global currentState
  if __verbose__:
    print('{0} release'.format(key))

  pageMode = pageSettings[currentState][MODE]

  # UP and DOWN case
  if key in [Key.up, Key.down]:
    if pageMode is PAGE_STYLE.NAVIGATION:
      moveCursorUpDown(currentState, key)

    if pageMode is PAGE_STYLE.JOG:
      if __verbose__:
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

  maxLength = len(stateMachine[state][DISPLAY])

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
    elif cursorIndex[state] == LCD_LEN-1:
        pageDisplayIndex[state] += 1
    # Your cursor is not at the bottom.
    else:
      cursorIndex[state] += 1

def DisplayLCD():
  ci      = cursorIndex[currentState]
  pdi     = pageDisplayIndex[currentState]
  displayList = stateMachine[currentState][DISPLAY]
  displayLen  = len(displayList)
  displayTexts = []

  # Get a list of strings to display.
  print("--------------------")
  if currentState == STATE.JOG_AXIS:
    jogIndex = cursorIndex[STATE.JOG] + pageDisplayIndex[STATE.JOG]
    axis = stateMachine[STATE.JOG][VALUE][jogIndex]
    displayTexts = LCD.DisplayJogAxis(axis)
  elif currentState == STATE.PINMAP_SINGLE:
    pinIndex = cursorIndex[STATE.PINMAP] + pageDisplayIndex[STATE.PINMAP]
    pin = stateMachine[STATE.PINMAP][VALUE][pinIndex]
    displayTexts = LCD.DisplayPinMapSingle(pin)
  # This is the default case with multiple entries.
  else:
    displayTexts = LCD.DisplayEntries(displayList, pdi, ci, displayLen)


  for i in range(LCD_LEN):
    print(displayTexts[i])
  print("--------------------")


  if __raspberry__ :
#    port.write('$C\r'.encode())

    for i in range(LCD_LEN):
      displayText = displayTexts[i]
      displayText = displayText + " " * (20 - len(displayText))      

      port.write(('$G,' + str(i%4+1) + ',1\r').encode())
      port.write(('$T,' + displayText + '\r').encode())


StartKeyListener()

while(1):
  time.sleep(1)
