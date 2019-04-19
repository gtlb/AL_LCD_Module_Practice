import Header as H
import datetime
import threading
import time
from threading import Lock
from Models.RunConfig import RunConfig as RC
from Constants.Enums import PwmConfig as PWM

RunConfig = RC.getInstance()

if H.__raspberry__:
  import RPi.GPIO as GPIO

  GPIO.setmode(GPIO.BCM)

  GPIO.setup(RunConfig.pwm[PWM.ON_OFF_PIN], GPIO.OUT, initial = GPIO.LOW)
  GPIO.setup(RunConfig.pwm[PWM.PWM_PIN], GPIO.OUT, initial = GPIO.LOW)


PWMThread = None
RTD = None

isRunPWM = False
isRunPWMLock = Lock()

pwmInst = None

def SetIsRunPWM(value):
  global isRunPWM, isRunPWMLock

  isRunPWMLock.acquire()
  isRunPWM = value
  isRunPWMLock.release()

def UpdateDutyCycle():
  if H.__raspberry__:
    global pwmInst

    pwmInst.ChangeDutyCycle(RunConfig.pwm[PWM.DUTY_CYCLE])

def StartPWM(rtd):
  global RTD
  RTD = rtd

  LogTempThread = threading.Thread(target = LogTemp)
  LogTempThread.daemon = True
  LogTempThread.start()

  PWMThread = threading.Thread(target = RunPWM)
  PWMThread.daemon = True
  SetIsRunPWM(True)
  PWMThread.start()

def StopPWM():
  SetIsRunPWM(False)

def LogTemp():
  fo = open(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ".txt", "w")
  while True:
    if not isRunPWM:
      fo.close()
      break

    fo.write(datetime.datetime.now().time().strftime('%Y-%m-%d %H:%M:%S:%f') + ": " + "{0:0.2f}C".format(RTD.temperature) + "\n")

    time.sleep(0.05)

def RunPWM():
  # Setup PWM
  if H.__raspberry__:
    global pwmInst

    GPIO.output(RunConfig.pwm[PWM.ON_OFF_PIN], GPIO.HIGH)
    pwmInst = GPIO.PWM(RunConfig.pwm[PWM.PWM_PIN], RunConfig.pwm[PWM.FREQUENCY])
    pwmInst.start(RunConfig.pwm[PWM.DUTY_CYCLE])

  trigger = False
  TARGET_TEMP_HIGH = 240
  TARGET_TEMP_LOW = 200

  while True:
    if not isRunPWM:
      # PWM Cleanup
      if H.__raspberry__:
        pwmInst.stop()
      break

    if H.__raspberry__:
      temp = float("{0:0.2f}".format(RTD.temperature))

      if temp > TARGET_TEMP_HIGH:
        trigger = True
        pwmInst.stop()
      elif trigger and temp < TARGET_TEMP_LOW:
        trigger = False
        pwmInst.start(RunConfig.pwm[PWM.DUTY_CYCLE])

    if H.__verbose__:
      print("PWM RUNNING " + str(RunConfig.pwm[PWM.DUTY_CYCLE]))

    time.sleep(1)
