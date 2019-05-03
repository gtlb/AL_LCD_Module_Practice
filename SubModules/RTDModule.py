import board
import busio
import digitalio
import adafruit_max31865

def Setup():
  spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
  cs = digitalio.DigitalInOut(board.D5)
  RTD = adafruit_max31865.MAX31865(spi, cs)

  return RTD
