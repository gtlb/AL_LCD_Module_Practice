import Header as H
import time
import SubModules.MoveModule as MoveModule
import SubModules.PWMModule as PWMModule
from Constants.Enums import ActName

# TODO: find a way to have a single source of resources
def HandleAct(runActName, runActArgs, RTD, jumpCallback):

  if H.__verbose__:
    print("Running {} act with args {}.".format(runActName, runActArgs))

  if runActName == ActName.MOVE_TO:
    HandleMoveTo(runActArgs)
  elif runActName == ActName.WAIT:
    HandleWait(runActArgs)
  elif runActName == ActName.IO:
    HandleIO(runActArgs)
  elif runActName == ActName.JUMP:
    HandleJump(runActArgs, jumpCallback)
  elif runActName == ActName.PWM:
    HandlePWM(runActArgs, RTD)
  elif runActName == ActName.PWM_SEQUENCE:
    HandlePWMSequence(runActArgs, RTD)
  elif runActName == ActName.PWM_MATRIX:
    HandlePWMMatrix(runActArgs, RTD)

  if H.__verbose__:
    print("Finished {} act.".format(runActName))

def HandleMoveTo(args):
  axis = args[0]
  direction = args[1]
  numSteps = args[2]
  delay = args[3]
  MoveModule.StartMoving(axis, direction, numSteps, delay)

  while MoveModule.GetIsMoving():
    time.sleep(0.5)

def HandleWait(args):
  time.sleep(args[0])

def HandleIO(args):
  if H.__raspberry__:
    import RPi.GPIO as GPIO
    GPIO.output(args[0], args[1])

def HandleJump(args, jumpCallback):
  # -1 because RunModule automatically increments one after this Act.
  jumpCallback(args[0]-1)

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
