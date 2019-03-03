import threading
import RPi.GPIO as GPIO

from threading import Lock

from Constants.Enums import Axis as AXIS
from Constants.Enums import Direction as DIR
from Constants.Enums import PinMap as PIN

isJogging = False
isJoggingLock = Lock()

joggingAxis = AXIS.X
pulseCounter = 0

def StartJog(axis, direction):
  global joggingAxis, pulseCounter

  GPIO.output(pinMap[axis][PIN.DIR], direction)

  SetIsJogging(True)
  joggingAxis = axis
  pulseCounter = 0

def StopJog():
  global isJogging
  SetIsJogging(False)

def SetIsJogging(value):
  global isJogging

  isJoggingLock.acquire()
  isJoggingLock = value
  isJoggingLock.release()

def JogHandler():
  global pulseCounter

  while True:
    if isJogging:
      GPIO.output(pinMap[joggingAxis][PIN.CLK], (pulseCounter+1)%2)
      pulseCounter += 1

      time.sleep(RunConfig.axisDelay[joggingAxis])

jogHandlerThread = threading.Thread(target = JogHandler)
jogHandlerThread.daemon = True
jogHandlerThread.start()
