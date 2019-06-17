import time
import board
import busio
import digitalio
import adafruit_max31865

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D25)  # Chip select of the MAX31865 board.
sensor = adafruit_max31865.MAX31865(spi, cs, wires=3)

i=0

while(True):
  if (i % 10) == 0:
    cs = digitalio.DigitalInOut(board.D24)  # Chip select of the MAX31865 board.
    sensor = adafruit_max31865.MAX31865(spi, cs, wires=3)

  if (i % 10) == 5:
    cs = digitalio.DigitalInOut(board.D25)  # Chip select of the MAX31865 board.
    sensor = adafruit_max31865.MAX31865(spi, cs, wires=3)

  print(sensor.temperature)
  time.sleep(1)
  i += 1
