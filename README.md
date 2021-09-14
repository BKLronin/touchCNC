# touchCNC
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

![Alt text](https://github.com/BKLronin/touchCNC/blob/815d2489f842d86d124fcf1924b28de70ac289a3/Screen.png "Preview")

Tested on latest Armbian stable https://www.armbian.com/odroid-c2/#kernels-archive-all

Based on
Python3
tkinter
pyserial

In some cases you have to manually install tkinter via apt and pyserial via pip.
