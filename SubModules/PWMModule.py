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

pwmMatrixCondition = [0, 0, 0]
pwmMatrixConditionLock = Lock()

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

def SetPWMMaxtrixCondition(value):
  global pwmMatrixCondition, pwmMatrixConditionLock

  pwmMatrixConditionLock.acquire()
  pwmMatrixCondition = value
  pwmMatrixConditionLock.release()

def GetPwmMatrixCurrentCondition():
  global pwmMatrixCondition, pwmMatrixConditionLock

  pwmMatrixConditionLock.acquire()
  temp = pwmMatrixCondition
  pwmMatrixConditionLock.release()

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


def StartPWMMatrix(rtd):
  global RTD
  RTD = rtd

  SetIsRunPWM(True)

  tempThread = threading.Thread(target = RunTemp)
  tempThread.daemon = True
  tempThread.start()

  LogTempThread = threading.Thread(target = LogTemp)
  LogTempThread.daemon = True
  LogTempThread.start()

  PWMThread = threading.Thread(target = RunPWMMatrix)
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

    if H.__raspberry__ and RTDTemp is not None:
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

def RunPWMMatrix():
  # Setup PWM
  if H.__raspberry__:
    global pwmInst

    GPIO.output(RunConfig.pwm[PWM.ON_OFF_PIN], GPIO.HIGH)
    pwmInst = GPIO.PWM(RunConfig.pwm[PWM.PWM_PIN], RunConfig.pwm[PWM.FREQUENCY])
    pwmInst.start(RunConfig.pwm[PWM.DUTY_CYCLE])

  lastThreeData = [(0.0, 0), (0.0, 0), (0.0, 0)]

  # TODO: Move to below
  temp = 150.0
  timestamp = 0
  lastPWMOutputIndex = -1
  while True:
    if not isRunPWM:
      # PWM Cleanup
      if H.__raspberry__:
        pwmInst.stop()
      break

    if not H.__raspberry__:
      temp += lastPWMOutputIndex - 0.5

    if H.__raspberry__ and RTDTemp is not None:
      temp = float("{0:0.2f}".format(RTDTemp))

    timestamp = time.time()

    # Track last three temperatures.
    lastThreeData[2] = lastThreeData[1]
    lastThreeData[1] = lastThreeData[0]
    lastThreeData[0] = (temp, timestamp)

    slope = GetSlope(lastThreeData)

    if H.__verbose__:
      print(lastThreeData)
      print("Slope: " + str(slope))

    [pwmOutputIndex, condition] = FindPWMOutputIndex(temp, slope)

    SetPWMMaxtrixCondition(condition)

    if pwmOutputIndex != lastPWMOutputIndex:
      if H.__verbose__:
        print("Set Duty Cycle To: " + str(RunConfig.pwm[PWM.DUTY_CYCLE_LIST][pwmOutputIndex]))

      if H.__raspberry__:
        pwmInst.ChangeDutyCycle(RunConfig.pwm[PWM.DUTY_CYCLE_LIST][pwmOutputIndex])

      lastPWMOutputIndex = pwmOutputIndex

    if H.__verbose__:
      print("PWM RUNNING " + str(RunConfig.pwm[PWM.DUTY_CYCLE]))

    time.sleep(1)

def GetSlope(tempData):
  slopeList = []
  for i in range(len(tempData)-1):
    tempDataX = tempData[i]
    tempDataY = tempData[i+1]

    if tempDataY[1] - tempDataX[1] == 0:
      slopeList.append(0)
      continue

    slope = (tempDataY[0] - tempDataX[0]) / (tempDataY[1] - tempDataX[1])
    slopeList.append(slope)

  return sum(slopeList) / (len(tempData)-1)

def FindPWMOutputIndex(currentTemp, currentSlope):
  pwmMatrixData = RunConfig.pwmMatrix
  # TODO: enum this
  tempRange = pwmMatrixData["Temperature"]
  slopeRange = pwmMatrixData["Slope"]
  outputMatrix = pwmMatrixData["Output"]

  tempIndex = 0
  for i in range(len(tempRange)-1):
    if currentTemp >= tempRange[i] and currentTemp < tempRange[i+1]:
      tempIndex = i
      break
  if currentTemp >= tempRange[-1]:
    tempIndex = len(tempRange)-1

  slopeIndex = 0
  for i in range(len(slopeRange)):
    if IsInside(currentSlope, slopeRange[i]):
      slopeIndex = i
      break

  return (outputMatrix[slopeIndex][tempIndex],
          [tempIndex, slopeIndex, outputMatrix[slopeIndex][tempIndex]])

def IsInside(value, range):
  return value >= range[0] and value < range[1]
