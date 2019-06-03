import Header as H
import time
import SubModules.PWMModule as PWMModule
from Constants.Enums import ActName

# TODO: find a way to have a single source of resources
def HandleAct(runActName, runActArgs, RTD):

  if H.__verbose__:
    print("Running {} act with args {}.".format(runActName, runActArgs))

  if runActName == ActName.MOVE_TO:
    print("Run MOVE_TO")
  elif runActName == ActName.WAIT:
    HandleWait(runActArgs)
  elif runActName == ActName.IO:
    HandleIO(runActArgs)
  elif runActName == ActName.PWM:
    HandlePWM(runActArgs, RTD)
  elif runActName == ActName.PWM_SEQUENCE:
    HandlePWMSequence(runActArgs)
  elif runActName == ActName.PWM_MATRIX:
    HandlePWMMatrix(runActArgs)

  if H.__verbose__:
    print("Finished {} act.".format(runActName))


def HandleWait(args):
  time.sleep(args[0])

def HandleIO(args):
  if H.__raspberry__:
    import RPi.GPIO as GPIO
    GPIO.output(args[0], args[1])

def HandlePWM(args, RTD):
  PWMModule.StartPWM(RTD, args[0], args[1], args[2])

def HandlePWMSequence(args):
  pass

def HandlePWMMatrix(args):
  pass
