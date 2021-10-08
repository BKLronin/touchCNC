# touchCNC -not ready for production - TESTING STAGE
GRBL 1.1 CNC Controller for ODROID C2 with VU PLus Touch Screen

Should run on any System wit at least 1024x600 Screen Resolution. 

- Jog 
- Zero positions 
- Job commands 
- Spindle Coolant, Tool and Macro commands 
- Gcode milling envelope preview (low cpu usage), 
- G28 Position
- Feed override
- terminal

![Screen](https://user-images.githubusercontent.com/6392076/133233601-8ef0e06f-e055-4677-8828-ed092aa37250.png)


Tested on latest Armbian stable https://www.armbian.com/odroid-c2/#kernels-archive-all

Based on
Python3
tkinter
pyserial

In some cases you have to manually install tkinter via apt and pyserial via pip.
