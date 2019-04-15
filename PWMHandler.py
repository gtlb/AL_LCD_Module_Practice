import threading
import time
from threading import Lock
from Models.RunConfig import RunConfig as RC
from Constants.Enums import PwmConfig as PWM

__verbose__ = False
__raspberry__ = False

if __raspberry__:
  import RPi.GPIO as GPIO

RunConfig = RC.getInstance()
PWMThread = None

isRunPWM = False
isRunPWMLock = Lock()

pwmInst = None

def SetIsRunPWM(value):
  global isRunPWM, isRunPWMLock

  isRunPWMLock.acquire()
  isRunPWM = value
  isRunPWMLock.release()

def UpdateDutyCycle():
  if __raspberry__:
    global pwmInst

    pwmInst.ChangeDutyCycle(RunConfig.pwm[PWM.DUTY_CYCLE])

def StartPWM():
  PWMThread = threading.Thread(target = RunPWM)
  PWMThread.daemon = True
  SetIsRunPWM(True)
  PWMThread.start()

def StopPWM():
  SetIsRunPWM(False)

def RunPWM():
  # Setup PWM
  if __raspberry__:
    global pwmInst
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(RunConfig.pwm[PWM.ON_OFF_PIN], GPIO.OUT, initial = GPIO.LOW)
    GPIO.setup(RunConfig.pwm[PWM.PWM_PIN], GPIO.OUT, initial = GPIO.LOW)

    GPIO.output(RunConfig.pwm[PWM.ON_OFF_PIN], GPIO.HIGH)
    pwmInst = GPIO.PWM(RunConfig.pwm[PWM.PWM_PIN], RunConfig.pwm[PWM.FREQUENCY])
    pwmInst.start(RunConfig.pwm[PWM.DUTY_CYCLE])

  while True:
    if not isRunPWM:
      # PWM Cleanup
      if __raspberry__:
        pwmInst.stop()
        GPIO.cleanup()
      break

    if __verbose__:
      print("PWM RUNNING " + str(RunConfig.pwm[PWM.DUTY_CYCLE]))

    time.sleep(1)
