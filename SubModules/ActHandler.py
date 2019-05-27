import Header as H
import time
import SubModules.PWMModule as PWMModule
import lcdModule
from Constants.Enums import ActName

def HandleAct(runActName, runActArgs):

  if H.__verbose__:
    print("Running {} act with args {}.".format(runActName, args))

  if runActName == ActName.MOVE_TO:
    print("Run MOVE_TO")
  elif runActName == ActName.WAIT:
    HandleWait(args)
  elif runActName == ActName.IO:
    HandleIO(args)
  elif runActName == ActName.PWM:
    HandlePWM(args)
  elif runActName == ActName.PWM_SEQUENCE:
    HandlePWMSequence(args)
  elif runActName == ActName.PWM_MATRIX:
    HandlePWMMatrix(args)

  if H.__verbose__:
    print("Finished {} act.".format(runActName))


def HandleWait(args):
  time.sleep(args[0])

def HandleIO(args):
  if H.__raspberry__:
    import RPi.GPIO as GPIO
    GPIO.output(args[0], args[1])

def HandlePWM(args):
  PWMModule.StartPWM(RTD, args[0], args[1], args[2])

def HandlePWMSequence(args):
  pass

def HandlePWMMatrix(args):
  pass
