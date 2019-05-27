import Header as H
import datetime
import threading
import time
import json
import Constants.Constants as C
from threading import Lock
from Models.RunConfig import RunConfig as RC
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

  while runIndex < len(runSequence):
    if not isRunSequence:
      break
      
    runAct = runSequence[runIndex]
    runActName = runAct['name']
    runActArgs = runAct['arguments']

    if H.__verbose__:
      print("Running: {} with args {}".format(runActName, runActArgs))

    time.sleep(1)

    runIndex += 1

  if H.__verbose__:
    print("Sequence {} Complete.".format(runSequenceTitle))

  pass
