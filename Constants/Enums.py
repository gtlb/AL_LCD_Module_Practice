def enum(**enums):
  return type('Enum', (), enums)

PinMap = enum(
  CLK = "CLK",
  DIR = "DIR",
  ENA = "ENA"
)

IO = enum(
  VALVE = "VALVE"
)

Axis = enum(
  X = "X",
  Y = "Y",
  Z = "Z"
)

Direction = enum(
  PLUS = 0,
  MINUS = 1
)

PageStyle = enum(
  NAVIGATION = "NAVIGATION",
  JOG = "JOG",
  EDIT = "EDIT"
)
