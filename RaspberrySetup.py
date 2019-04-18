import RPi.GPIO as GPIO
from Constants.Enums import Axis as AXIS
from Constants.Enums import Direction as DIR
from Constants.Enums import PinMap as PIN
from Models.RunConfig import RunConfig as RC

def Setup():
  RunConfig = RC.getInstance()

  #### Some Configurations ####
  pinSol = RunConfig.pinSol
  pinMap = RunConfig.pinMap
  #############################

  #### GPIO Initial Setup ####
  GPIO.setmode(GPIO.BCM)

  GPIO.setup(pinMap[AXIS.X][PIN.CLK], GPIO.OUT, initial = GPIO.LOW)
  GPIO.setup(pinMap[AXIS.X][PIN.DIR], GPIO.OUT, initial = GPIO.LOW)
  GPIO.setup(pinMap[AXIS.X][PIN.ENA], GPIO.OUT, initial = GPIO.HIGH)

  GPIO.setup(pinMap[AXIS.Y][PIN.CLK], GPIO.OUT, initial = GPIO.LOW)
  GPIO.setup(pinMap[AXIS.Y][PIN.DIR], GPIO.OUT, initial = GPIO.LOW)
  GPIO.setup(pinMap[AXIS.Y][PIN.ENA], GPIO.OUT, initial = GPIO.LOW)

  GPIO.setup(pinMap[AXIS.Z][PIN.CLK], GPIO.OUT, initial = GPIO.LOW)
  GPIO.setup(pinMap[AXIS.Z][PIN.DIR], GPIO.OUT, initial = GPIO.LOW)
  GPIO.setup(pinMap[AXIS.Z][PIN.ENA], GPIO.OUT, initial = GPIO.LOW)

  GPIO.setup(pinSol, GPIO.OUT, initial = GPIO.LOW)
  ############################

def cleanup():
  GPIO.cleanup()

