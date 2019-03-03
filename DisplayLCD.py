LCD_LEN = 4

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
