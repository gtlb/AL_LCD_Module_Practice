__verbose__   = False
__raspberry__ = False

import sys
if len(sys.argv) == 2 and sys.argv[1] in ['-v', '-V']:
  __verbose__ = True

# Figure out if the program is running on RaspberryPi or Windows.
try:
  import RPi.GPIO as gpio
  print("Raspberry Pi")
  __raspberry__ = True
except (ImportError, RuntimeError):
  print("Windows")
  __raspberry__ = False
