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

def StartMovingTrapezoid(axis, direction, numSteps, delay,
                         stepsAccelerate, stepsDecelerate, delayStart):
  SetIsMoving(True)

  moveTrapThread = threading.Thread(
                     target = RunMoveTrapezoid,
                     args=[axis, direction, numSteps, delay,
                           stepsAccelerate, stepsDecelerate, delayStart])
  moveTrapThread.daemon = True
  moveTrapThread.start()

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


def RunMoveTrapezoid(axis, direction, numSteps, delayTarget,
                     stepsAccelerate, stepsDecelerate, delayStart):
  global currentPulseMap

  if H.__raspberry__:
    GPIO.output(pinMap[axis][PIN.DIR], direction)

  # TODO: config these
  # stepsAccelerate = 200
  # stepsDecelerate = 200
  # delayStart = 0.1

  runFinished = True
  delay = delayStart
  for i in range(numSteps):
    if not isMoving:
      runFinished = False

      if H.__verbose__:
        print("Moving Trapezoid has been aborted.")

      break

    # Determining delay

    # Case 1 : Cannot accelerate to the max.
    sa = stepsAccelerate
    sd = stepsDecelerate
    if stepsAccelerate + stepsDecelerate >= numSteps:
      accelerateRange = numSteps / (sa + sd) * sa
      ar = accelerateRange
      print("Accelerate Range: {}".format(ar))
      ratio = ar / sa
      newDelayTarget = delayStart * (1 - ratio) + delayTarget * ratio
      print("New Delay Target: {}".format(newDelayTarget))

      if i < accelerateRange:
        print("Accelerate")
        ratio = i / accelerateRange
        delay = delayStart * (1 - ratio) + newDelayTarget * ratio
      else:
        print("Decelerate")
        ratio = (i - ar) / (numSteps - ar)
        delay = newDelayTarget * (1 - ratio) + delayStart * ratio

    # Case 2 : Can accelerate to the max.
    else:
      if i <= stepsAccelerate:
        print("Accelerate")
        ratio = i / stepsAccelerate
        delay = delayStart * (1 - ratio) + delayTarget * ratio
      elif i >= numSteps - stepsDecelerate:
        print("Decelerate")
        ratio = (i - (numSteps - stepsDecelerate)) / stepsDecelerate
        delay = delayTarget * (1 - ratio) + delayStart * ratio
      else:
        print("Stable")
        delay = delayTarget

    print("Step: {}, Delay: {}".format(i, delay))

    if H.__raspberry__:
      GPIO.output(pinMap[axis][PIN.CLK], GPIO.HIGH)
    time.sleep(delay)

    if H.__raspberry__:
      GPIO.output(pinMap[axis][PIN.CLK], GPIO.LOW)
    time.sleep(delay)

  if runFinished and H.__verbose__:
    print("Moving Trapezoid {} by {} Complete.".format(axis, numSteps))

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
