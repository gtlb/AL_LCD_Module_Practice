import Header as H
import datetime
import threading
import time
import json
import Constants.Constants as C
import SubModules.ActHandler as ActHandler
from threading import Lock
from Models.RunConfig import RunConfig as RC
from Constants.Enums import ActName
from Constants.Enums import PwmConfig as PWM

RunConfig = RC.getInstance()

runIndex = 0
runIndexLock = Lock()

isRunSequence = False
isRunSequenceLock = Lock()

runSequence = None
runSequenceTitle = None

def StartRunSequence(sequenceTitle):
  global runSequence, runSequenceTitle

  runSequence = LoadRunSequence(sequenceTitle)
  runSequenceTitle = sequenceTitle

  SetRunIndex(0)
  SetIsRunSequence(True)

  runThread = threading.Thread(target = RunSequence)
  runThread.daemon = True
  runThread.start()

def StopRunSequence():
  SetIsRunSequence(False)

def SetRunIndex(index):
  global runIndex, runIndexLock

  runIndexLock.acquire()
  runIndex = index
  runIndexLock.release()

def SetIsRunSequence(value):
  global isRunSequence, isRunSequenceLock

  isRunSequenceLock.acquire()
  isRunSequence = value
  isRunSequenceLock.release()

def LoadRunSequence(sequenceTitle):
  fp = open("{}{}".format(C.RUN_SEQUENCES_FILEPATH, sequenceTitle))
  return json.load(fp)


def RunSequence():
  global runIndex, runSequence, runSequenceTitle

  SetupRaspberryPi(runSequence)

  while runIndex < len(runSequence):
    if not isRunSequence:
      break

    runAct = runSequence[runIndex]
    runActName = runAct['name']
    runActArgs = runAct['arguments']

    ActHandler.HandleAct(runActName, runActArgs)

    time.sleep(0.1)

    runIndex += 1

  if H.__verbose__:
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
