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
    HandlePWMSequence(runActArgs, RTD)
  elif runActName == ActName.PWM_MATRIX:
    HandlePWMMatrix(runActArgs, RTD)

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

  while PWMModule.GetIsRunPWM():
    time.sleep(0.5)

def HandlePWMSequence(args, RTD):
  PWMModule.StartPWMSequence(RTD, args[0], args[1], args[2])

  while PWMModule.GetIsRunPWM():
    time.sleep(0.5)

def HandlePWMMatrix(args, RTD):
  PWMModule.StartPWMMatrix(RTD, args[0], args[1], args[2])

  while PWMModule.GetIsRunPWM():
    time.sleep(0.5)
