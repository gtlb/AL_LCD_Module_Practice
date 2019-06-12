import Header as H
import threading
import time
from threading import Lock
from Constants.Enums import Axis as AXIS
from Constants.Enums import Direction as DIR
from Constants.Enums import PinMap as PIN
from Models.RunConfig import RunConfig as RC

RunConfig = RC.getInstance()

pinMap = RunConfig.pinMap

currentPulseMap = {}
currentPulseMapLock = Lock()

homeTimeLimit = None

if H.__raspberry__:
  import RPi.GPIO as GPIO

isMoving = False
isMovingLock = Lock()

def SetIsMoving(value):
  global isMoving, isMovingLock

  isMovingLock.acquire()
  isMoving = value
  isMovingLock.release()

def GetIsMoving():
  global isMoving, isMovingLock

  value = None

  isMovingLock.acquire()
  value = isMoving
  isMovingLock.release()

  return value

def StopMoving():
  # Need to stop PWM if it is running.
  SetIsMoving(False)

def StartMoving(axis, direction, numSteps, delay):
  SetIsMoving(True)

  moveThread = threading.Thread(target = RunMove,
                                args=[axis, direction, numSteps, delay])
  moveThread.daemon = True
  moveThread.start()

def StartHoming(axis, direction, delay, timeout):
  global homeTimeLimit

  SetIsMoving(True)

  if timeout is not None:
    homeTimeLimit = time.time() + timeout

  homeThread = threading.Thread(target = RunHome, args=[axis, direction, delay])
  homeThread.daemon = True
  homeThread.start()

def UpdatePulse(axis, pulse):
  global currentPulseMap
  currentPulseMapLock.acquire()
  currentPulseMap[axis] = pulse
  currentPulseMapLock.release()

def GetPulse(axis):
  global currentPulseMap
  value = None

  currentPulseMapLock.acquire()

  if axis not in currentPulseMap.keys():
    currentPulseMap[axis] = 0
  value = currentPulseMap[axis]

  currentPulseMapLock.release()

  return value


def RunMove(axis, direction, numSteps, delay):
  global currentPulseMap

  if H.__raspberry__:
    GPIO.output(pinMap[axis][PIN.DIR], direction)

  runFinished = True
  for i in range(numSteps * 2):
    if not isMoving:
      runFinished = False

      if H.__verbose__:
        print("Moving has been aborted.")

      break

    if H.__raspberry__:
      GPIO.output(pinMap[axis][PIN.CLK], (i+1)%2)

    time.sleep(delay)

  if runFinished and H.__verbose__:
    print("Moving {} by {} Complete.".format(axis, numSteps))

  SetIsMoving(False)

  UpdatePulse(axis, GetPulse(axis) + numSteps)

def RunHome(axis, direction, delay):
  global currentPulseMap, homeTimeLimit

  homeSensor = None
  runFinished = True

  if H.__raspberry__:
    GPIO.output(pinMap[axis][PIN.DIR], direction)
    sensorPin = pinMap[axis][PIN.HOME]

  i = 0
  while (GPIO.input(sensorPin)):
    if not isMoving:
      runFinished = False
      if H.__verbose__:
        print("Homing has been aborted.")
      break

    if homeTimeLimit is not None and homeTimeLimit < time.time():
      runFinished = False
      if H.__verbose__:
        print("Homing has been timed out.")
      break

    if H.__raspberry__:
      GPIO.output(pinMap[axis][PIN.CLK], (i+1)%2)
      i += 1

    time.sleep(delay)

  if runFinished and H.__verbose__:
    print("Homing {} Complete.".format(axis))

  SetIsMoving(False)

  UpdatePulse(axis, 0)
