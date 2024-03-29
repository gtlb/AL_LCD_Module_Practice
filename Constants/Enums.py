def enum(**enums):
  return type('Enum', (), enums)

PinMap = enum(
  CLK = "CLK",
  DIR = "DIR",
  ENA = "ENA",
  HOME = "HOME"
)

IO = enum(
  VALVE = "VALVE"
)

Axis = enum(
  X = "X",
  Y = "Y",
  Z = "Z",
  A = "A",
  B = "B",
  C = "C"
)

Direction = enum(
  PLUS = 0,
  MINUS = 1
)

PageStyle = enum(
  NAVIGATION = "NAVIGATION",
  JOG = "JOG",
  PWM = "PWM",
  PWM_SIMPLE = "PWM_SIMPLE",
  PWM_SEQUENCE = "PWM_SEQUENCE",
  PWM_MATRIX = "PWM_MATRIX",
  EDIT = "EDIT",
  RUN_SEQUENCE = "RUN_SEQUENCE"
)

PwmConfig = enum(
  ON_OFF_PIN = "OnOffPin",
  PWM_PIN = "PWMPin",
  FREQUENCY = "Frequency",
  DUTY_CYCLE = "DutyCycle",
  FREQUENCY_LIST = "FrequencyList",
  DUTY_CYCLE_LIST = "DutyCycleList"
)

STATE = enum(
  MAIN           = "MAIN",
  JOG            = "JOG",
  JOG_AXIS       = "JOG_AXIS",

  RUN            = "RUN",
  RUN_SEQUENCE   = "RUN_SEQUENCE",

  SETTINGS       = "SETTINGS",
  PWM_FREQUENCY  = "PWM_FREQUENCY",
  PWM_DUTY_CYCLE = "PWM_DUTY_CYCLE",

  PINMAP         = "PINMAP",
  PINMAP_SINGLE  = "PINMAP_SINGLE",

  PWM            = "PWM",
  PWM_SIMPLE     = "PWM_SIMPLE",
  PWM_SEQUENCE   = "PWM_SEQUENCE",
  PWM_MATRIX     = "PWM_MATRIX"
)

ActName = enum(
  MOVE_TO      = "MOVE_TO",
  MOVE_TO_TRAP = "MOVE_TO_TRAP",
  HOME         = "HOME",
  WAIT         = "WAIT",
  IO           = "IO",
  PWM          = "PWM",
  PWM_SIMPLE   = "PWM_SIMPLE",
  PWM_SEQUENCE = "PWM_SEQUENCE",
  PWM_MATRIX   = "PWM_MATRIX",
  JUMP         = "JUMP"
)
