from Constants.Enums import PinMap as PIN
from Models.RunConfig import RunConfig as RC

LCD_LEN = 4

RunConfig = RC.getInstance()
pinMap = RunConfig.pinMap

def DisplayJogAxis(axis):
  displayTexts = []
  displayTexts.append("JOG " + axis)
  displayTexts.append(" ")
  displayTexts.append("^ : Up Arrow")
  displayTexts.append("v : Down Arrorw")

  return displayTexts

def DisplayPinMapSingle(pin):
  displayTexts = []

  displayTexts.append("PIN " + pin)

  if pin in pinMap.keys():
    displayTexts.append(PIN.CLK + ": " + str(pinMap[pin][PIN.CLK]))
    displayTexts.append(PIN.DIR + ": " + str(pinMap[pin][PIN.DIR]))
    displayTexts.append(PIN.ENA + ": " + str(pinMap[pin][PIN.ENA]))
  else:
    displayTexts.append(" ")
    displayTexts.append(" ")
    displayTexts.append(" ")

  return displayTexts

def DisplayEntries(displayList, pdi, ci, totalEntryNum):
  displayTexts = []

  for i in range(LCD_LEN):
    if pdi + i < totalEntryNum:
      if i == ci:
        displayTexts.append("> " + displayList[pdi + i])
      else:
        displayTexts.append("  " + displayList[pdi + i])
    else:
      displayTexts.append("  ")

  return displayTexts
