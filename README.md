# touchCNC
GRBL 1.1 CNC Controller for ODROID C2 with VU PLus Touch Screen

Should run on any System wit at least 1024x600 Screen Resolution. 

- Jog 
- Zero positions 
- Job commands 
- Spindle Coolant, Tool
- Gcode milling envelope preview (low cpu usage), 
- G28 Position
- Feed override (soon)
- terminal

![Screenshot_20231222_205706](https://github.com/BKLronin/touchCNC/assets/6392076/b57899df-8c59-4353-a41a-548273e79a59)


Tested on latest Armbian stable https://www.armbian.com/odroid-c2/#kernels-archive-all

Based on
Python3
tkinter
pyserial
gerbil
gcodemachine

In some cases you have to manually install tkinter via apt and pyserial via pip.

