# touchCNC 1.0
GRBL 1.1 CNC Controller for ODROID C2 with VU PLus Touch Screen or Linux Desktop

Should run on any System wit at least 1024x600 Screen Resolution. 

- Jog 
- Zero positions 
- Job commands 
- Spindle Coolant, Tool and Macro commands 
- Gcode milling envelope preview 
- G28 Position
- Feed override (Not yet working)
- terminal
- Laser status and switch

![Screen](https://user-images.githubusercontent.com/6392076/133233601-8ef0e06f-e055-4677-8828-ed092aa37250.png)

- Tested on latest Armbian stable https://www.armbian.com/odroid-c2/#kernels-archive-all
- Tested on Manjaro 
- Using cncpro v3 with grbl1.1f

## Clone to your PC
`git clone https://github.com/BKLronin/touchCNC.git`

## Install 
- (Create env)
- In folder enter:
`pip install requirements.txt`

## Run 
`python cnc_gerbil.py`
or
`cd dist`
`./cnc_gerbil`

### Based on:
Python3
tkinter
pyserial
gerbil

