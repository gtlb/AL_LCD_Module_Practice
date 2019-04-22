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

RTDTemp = None
RTDTempLock = Lock()

pwmInst = None

pwmSequenceIndex = 0
pwmSequenceIndexLock = Lock()

def SetIsRunPWM(value):
  global isRunPWM, isRunPWMLock

  isRunPWMLock.acquire()
  isRunPWM = value
  isRunPWMLock.release()

def SetRTDTemp(value):
  global RTDTemp, RTDTempLock

  RTDTempLock.acquire()
  RTDTemp = value
  RTDTempLock.release()

def GetRTDTemp():
  global RTDTemp, RTDTempLock

  RTDTempLock.acquire()
  temp = RTDTemp
  RTDTempLock.release()

  return temp

def SetPWMSequenceIndex(value):
  global pwmSequenceIndex, pwmSequenceIndexLock

  pwmSequenceIndexLock.acquire()
  pwmSequenceIndex = value
  pwmSequenceIndexLock.release()

def GetPWMSequenceIndex():
  global pwmSequenceIndex, pwmSequenceIndexLock

  pwmSequenceIndexLock.acquire()
  temp = pwmSequenceIndex
  pwmSequenceIndexLock.release()

  return temp

def UpdateDutyCycle():
  if H.__raspberry__:
    global pwmInst

    pwmInst.ChangeDutyCycle(RunConfig.pwm[PWM.DUTY_CYCLE])

def StartPWM(rtd):
  global RTD
  RTD = rtd

  SetIsRunPWM(True)

  tempThread = threading.Thread(target = RunTemp)
  tempThread.daemon = True
  tempThread.start()

  LogTempThread = threading.Thread(target = LogTemp)
  LogTempThread.daemon = True
  LogTempThread.start()

  PWMThread = threading.Thread(target = RunPWM)
  PWMThread.daemon = True
  PWMThread.start()

def StartPWMSequence(rtd):
  global RTD
  RTD = rtd

  SetIsRunPWM(True)

  tempThread = threading.Thread(target = RunTemp)
  tempThread.daemon = True
  tempThread.start()

  LogTempThread = threading.Thread(target = LogTemp)
  LogTempThread.daemon = True
  LogTempThread.start()

  PWMThread = threading.Thread(target = RunPWMSequence)
  PWMThread.daemon = True
  PWMThread.start()

def StopPWM():
  SetIsRunPWM(False)

def RunTemp():
  while True:
    if not isRunPWM:
      break

    if H.__raspberry__:
      SetRTDTemp(RTD.temperature)

    if H.__verbose__:
      print("Temp. Measured")

    time.sleep(0.2)

def LogTemp():
  fo = open(str(RunConfig.pwm[PWM.DUTY_CYCLE]) + "_"
    + datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S') + ".txt", "w")

  while True:
    if not isRunPWM:
      fo.close()
      break

    temp = "N/A"
    delay = 1

    if H.__raspberry__ and RTDTemp is not None:
      temp = "{0:0.2f}C".format(RTDTemp)
      delay = 0.5

    fo.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
      + ": " + temp + "\n")

    if H.__verbose__:
      print("File Write")

    time.sleep(delay)

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
      temp = float("{0:0.2f}".format(RTDTemp))

      if temp > TARGET_TEMP_HIGH:
        trigger = True
        pwmInst.stop()
      elif trigger and temp < TARGET_TEMP_LOW:
        trigger = False
        pwmInst.start(RunConfig.pwm[PWM.DUTY_CYCLE])

    if H.__verbose__:
      print("PWM RUNNING " + str(RunConfig.pwm[PWM.DUTY_CYCLE]))

    time.sleep(1)

def RunPWMSequence():
  # Setup PWM
  if H.__raspberry__:
    global pwmInst

    GPIO.output(RunConfig.pwm[PWM.ON_OFF_PIN], GPIO.HIGH)
    pwmInst = GPIO.PWM(RunConfig.pwm[PWM.PWM_PIN], RunConfig.pwm[PWM.FREQUENCY])
    pwmInst.start(RunConfig.pwm[PWM.DUTY_CYCLE])

  SetPWMSequenceIndex(0)
  lastThreeTemp = [0.0, 0.0, 0.0]

  # TODO: Move to below
  temp = 0.0
  while True:
    if not isRunPWM:
      # PWM Cleanup
      if H.__raspberry__:
        pwmInst.stop()
      break

    if H.__raspberry__:
      temp = float("{0:0.2f}".format(RTDTemp))

    # Track last three temperatures.
    lastThreeTemp[2] = lastThreeTemp[1]
    lastThreeTemp[1] = lastThreeTemp[0]
    lastThreeTemp[0] = temp

    if H.__verbose__:
      print(lastThreeTemp)

    averageLastTemp = (lastThreeTemp[1] + lastThreeTemp[2]) / 2

    # TODO: Enum this
    direction = "UP" if averageLastTemp < temp else "DOWN"
    [targetTemp, targetDir, level] = RunConfig.pwmSequence["Sequence"][GetPWMSequenceIndex()]

    if (direction == targetDir) \
      and ((direction == "UP" and targetTemp < temp) or (direction == "DOWN" and targetTemp > temp)):
      if GetPWMSequenceIndex() < len(RunConfig.pwmSequence["Sequence"])-1:
        SetPWMSequenceIndex(GetPWMSequenceIndex() + 1)

      if H.__verbose__:
        print("Set Duty Cycle To: " + str(RunConfig.pwm[PWM.DUTY_CYCLE_LIST][level]))

      if H.__raspberry__:
        pwmInst.ChangeDutyCycle(RunConfig.pwm[PWM.DUTY_CYCLE_LIST][level])

    if H.__verbose__:
      print("PWM RUNNING " + str(RunConfig.pwm[PWM.DUTY_CYCLE]))

    time.sleep(1)
