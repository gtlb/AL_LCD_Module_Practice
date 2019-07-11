import Header as H
import datetime
import threading
import time
import json
import Constants.Constants as C
import SubModules.ActHandler as ActHandler
import SubModules.MoveModule as MoveModule
import SubModules.PWMModule as PWMModule
from threading import Lock
from Models.RunConfig import RunConfig as RC
from Constants.Enums import ActName
from Constants.Enums import PwmConfig as PWM

RunConfig = RC.getInstance()

RTD = None

runIndex = 0
runIndexLock = Lock()

isRunSequence = False
isRunSequenceLock = Lock()

runSequence = None
runSequenceTitle = None

displayLCDCallback = None

def StartRunSequence(sequenceTitle, rtd):
  global runSequence, runSequenceTitle, RTD

  RTD = rtd

  runSequence = LoadRunSequence(sequenceTitle)
  runSequenceTitle = sequenceTitle

  SetRunIndex(0)
  SetIsRunSequence(True)

  #RunSequence() ---> function call also runs well for one motor   
  runThread = threading.Thread(target = RunSequence)
  runThread.daemon = True
  runThread.start()

def StopRunSequence():
  # Need to stop PWM if it is running.
  PWMModule.StopPWM()
  MoveModule.StopMoving()
  SetIsRunSequence(False)

def SetRunIndex(index):
  global runIndex, runIndexLock

  runIndexLock.acquire()
  runIndex = index
  runIndexLock.release()

def GetRunIndex():
  global runIndex, runIndexLock

  runIndexLock.acquire()
  value = runIndex
  runIndexLock.release()

  return value

def GetRunText():
  global runSequence, runIndex
  value = None

  runIndexLock.acquire()
  if runIndex < len(runSequence):
    value = runSequence[runIndex]['name']
  else:
    value = "Finished"
  runIndexLock.release()

  return value

def SetDisplayLCDCallback(callback):
  global displayLCDCallback

  displayLCDCallback = callback

def SetIsRunSequence(value):
  global isRunSequence, isRunSequenceLock

  isRunSequenceLock.acquire()
  isRunSequence = value
  isRunSequenceLock.release()

def LoadRunSequence(sequenceTitle):
  fp = open("{}{}".format(C.RUN_SEQUENCES_FILEPATH, sequenceTitle))
  return json.load(fp)


def RunSequence():
  global runIndex, runSequence, runSequenceTitle, RTD
  print('RunSequenc() executing ---')

  SetupRaspberryPi(runSequence)

  runFinished = True
  while runIndex < len(runSequence):
    if not isRunSequence:
      runFinished = False

      # As of now, sequence does not abort immediately.
      if H.__verbose__:
        print("Sequence {} Aborted.".format(runSequenceTitle))
      break

    runAct = runSequence[runIndex]
    runActName = runAct['name']
    runActArgs = runAct['arguments']

    # TODO: Currently PWM is non-blocking
    ActHandler.HandleAct(runActName, runActArgs, RTD, SetRunIndex)

    time.sleep(0.1)

    runIndex += 1
    displayLCDCallback()

  if runFinished and H.__verbose__:
    print("Sequence {} Complete.".format(runSequenceTitle))

  pass

def SetupRaspberryPi(runSequence):

  if H.__raspberry__:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)

  pinList = set()

  for act in runSequence:
    if act['name'] == ActName.IO:
      pinList.add(act['arguments'][0])

  for pin in pinList:
    if H.__raspberry__:
      GPIO.setup(pin, GPIO.OUT, initial = GPIO.LOW)
