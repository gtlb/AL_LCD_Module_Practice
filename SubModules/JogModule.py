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

if H.__raspberry__:
  import RPi.GPIO as GPIO

isJogging = False
isJoggingLock = Lock()

joggingAxis = AXIS.X
pulseCounter = 0

def StartJog(axis, direction):
  global joggingAxis, pulseCounter

  GPIOOutput(pinMap[axis][PIN.DIR], direction)

  SetIsJogging(True)
  joggingAxis = axis
  pulseCounter = 0

def StopJog():
  SetIsJogging(False)

def SetIsJogging(value):
  global isJogging, isJoggingLock

  isJoggingLock.acquire()
  isJogging = value
  isJoggingLock.release()

def JogHandler():
  global pulseCounter

  while True:
    if isJogging:
      if H.__verbose__:
        print("Jogging in Axis: " + joggingAxis)

      GPIOOutput(pinMap[joggingAxis][PIN.CLK], (pulseCounter+1)%2)
      pulseCounter += 1

      time.sleep(RunConfig.axisDelay[joggingAxis])
    else:
      time.sleep(1)

jogHandlerThread = threading.Thread(target = JogHandler)
jogHandlerThread.daemon = True
jogHandlerThread.start()

def GPIOOutput(pin, value):
  if H.__raspberry__:
    GPIO.output(pin, value)
