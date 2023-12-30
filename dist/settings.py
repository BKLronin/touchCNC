
# The resolution of your SBC-screen
resolution = '1024x600+0+0'

# When running on SBC with touch set to: True
set_fullscreen = False

# Platform dependent
portlist = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyUSB1', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3',
                     '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3']
# Where the file dialog points to. Ideally some Nextcloud folder or Samba share etc.
basepath = '/home/'

# Machine commands
spindle_on = 'M3S1000'
spindle_off = 'M5'
cooling_on = 'M8'
cooling_off = 'M9'
toolchange = 'G10 P0 L20 X0 Y0 Z0'

# Table Info Text
table_text = 'Fräsbereich 300mm x 300mm'
