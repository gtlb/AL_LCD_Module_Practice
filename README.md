# AL Cooker

This repository contains code for Avocado Lab's LCD module.
The program allows users to
1. Move Axis (X, Y, Z)
2. Run Induction Module


## Getting Started

The program is divided into
1. Core Logic : lcdModule.py
2. Sub Modules : SubModules/DisplayModule.py, JogModule.py, PWMModule.py, ...
3. Configurations : Config/Config.ini, PWMSequence.json, PWMMatrix.json

Core Logic contains all logic involving setting up motors and IOs,
triggering LCD displays, and sending signals to the induction module.

Sub Modules are responsible for runinng logic for specific purposes.  
`DisplayModule.py` handles sending signal to LCD display.  
`JogModule.py` handles sending step signals to motor drivers.  
`PWMModule.py` handles sending signals to Induction PWM drivers.  

Configurations allow users to configure necessary settings for the LCD Module.  
`Config.ini` inclues,
1. Motor related configs: pinmap, motor step delays, ...
2. PWM related configs: duty cycle, frequency, ...

`PWMSequence.json` specifices a sequence of (target temperature, coming direction, pwm level) triplets to run the
induction module with a desired PWM sequence.

`PWMMatrix.json` specifies a map of how the induction module should act
given current temperature and slope (temperature change / time).
2D matrix is constructed with Temperature (X-Axis) and Slope (Y-Axis).
`Output` specifies which pwm level to use upon reaching such condition.
