import ast
import configparser
import json
import Constants.Constants as C
from os import listdir
from pynput.keyboard import Key
from Constants.Enums import Axis as AXIS
from Constants.Enums import Direction as DIR
from Constants.Enums import PinMap as PIN
from Constants.Enums import PwmConfig as PWM

class Globals:
  __instance = None

  @staticmethod
  def getInstance():
    if Globals.__instance == None:
      Globals()
    return Globals.__instance

  def __init__(self):
    if Globals.__instance != None:
      raise Exception("Initialize called on an initialized singleton.")
