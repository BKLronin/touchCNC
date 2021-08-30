import serial
import time
from tkinter import *
import serial.tools.list_ports
from tkinter import filedialog as fd

grbl = 0
i = 10
GCODE = 0
AXIS = 'X'
states = {'M3': '0', 'M8':'0', 'M6':'0'} #Spindle, Coolant

def grblConnect2():
    global grbl

    #Serial Connection
    locations=['/dev/ttyACM0','/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyACM1','/dev/ttyACM2','/dev/ttyACM3',
        '/dev/ttyS0','/dev/ttyS1','/dev/ttyS2','/dev/ttyS3']
    
    for device in locations:
            try:
                #print([comport.device for comport in serial.tools.list_ports.comports()])
                print ("Trying...",device)
                grbl = serial.Serial(port= device, baudrate= 115200, timeout =.1)
                #grbl.open()
                #print(grbl.readline())
                grbl.write(str.encode("\r\n\r\n"))
                time.sleep(2)   # Wait for grbl to initialize
                grbl.flushInput()  # Flush startup text in serial input
                connect_ser.config(bg='green')
                #print("connected")

                break
            except:
                #print ("Failed to connect on",device)
                grbl = 0

    # Stream g-code to grbl
    #Stream GCODE from -https://onehossshay.wordpress.com/2011/08/26/grbl-a-simple-python-interface/-

def displayPosition(grbl):
    grbl_command = '?'
    grbl.write(str.encode(grbl_command + '\n'))
    position = grbl.readline()
    print("position", position)
    

def jogWrite(grbl,AXIS, CMD, scale):   
    DECIMAL = [0.1,1,10,100]
    scale = increments.get()
    MOVE = int(CMD) * DECIMAL[scale -1]     
    grbl_command = ('$J=G91' +' ' + AXIS + str(MOVE) + ' '+ 'F100')    
    #print(grbl_command)
    grbl.write(str.encode(grbl_command + '\n'))
    grbl_out = grbl.readline() # Wait for grbl response with carriage return
    #print(grbl_out.strip())
    infoScreen(grbl_command)
    infoScreen(grbl_out)

def directWrite(grbl, CMD):
    grbl_command = CMD
    grbl.write(str.encode(grbl_command + '\n'))
    grbl_out = grbl.readline() # Wait for grbl response with carriage return
    infoScreen(grbl_command)
    infoScreen(grbl_out)

def latchWrite(grbl, CMD):
    global states 
    if states[CMD] == '0':
        states[CMD] = '1'        
        if CMD == 'M3':
            spindle.config(bg='red')
        if CMD == 'M6':
            tool.config(bg = 'yellow')

    else:
        states[CMD] ='0'
        if CMD == 'M3':
            spindle.config(bg='green')
        if CMD == 'M6':
            tool.config(bg='grey')
    
    if CMD == 'M3':
        grbl_command = (CMD * int(states[CMD]))    
    
    if CMD == 'M8':
        if states['M8'] == '1':
            grbl_command = (CMD)
            coolant.config(bg ='blue')
        else:
            grbl_command = ('M7')
            coolant.config(bg ='grey')
    else:
        grbl_command = (CMD)     
    
    #grbl_command = (CMD * int(states[CMD]) )   
    print(grbl_command)
    print(states)
    grbl.write(str.encode(grbl_command + '\n'))
    grbl_out = grbl.readline() # Wait for grbl response with carriage return
    infoScreen(grbl_command)
    infoScreen(grbl_out)
    
def zeroWrite(grbl, CMD, AXIS):
    grbl_command = (CMD + ' ' + AXIS + '0')
    grbl.write(str.encode(grbl_command + '\n'))
    grbl_out = grbl.readline() # Wait for grbl response with carriage return
    infoScreen(grbl_command)
    infoScreen(grbl_out)

def terminalWrite(grbl):
    grbl_command = terminal.get()
    #print(grbl_command)
    grbl.write(str.encode(grbl_command + '\n'))
    grbl_out = grbl.readline() # Wait for grbl response with carriage return
    #print(grbl_out.strip())
    infoScreen(grbl_out)

def infoScreen(data):
    global i
    terminalFrame = Frame(terminal_recv, bg = 'white')
    terminal_recv.create_window(10,i, window = terminalFrame, anchor = 'nw')
    Label(terminalFrame, text = data, font = ('Calibri',10), bg ='white', fg ='black').pack()
    i += 22
    if i >=400:
        i=10
        terminal_recv.delete("all")

def openGCODE():
    global GCODE

    filetypes = (('GCODE', '*.nc'),('All files', '*.*'))
    GCODE = fd.askopenfile(title='Open a file', initialdir='/home/thomash/Environments/cnc/', filetypes=filetypes)
    
    if GCODE != 0:
        fopen.config(bg='green')
    else:
        fopen.config(bg = 'grey')
      
    build_xy = findEnvelope()
    mill_table.create_rectangle(build_xy[0],build_xy[1], fill = 'blue', stipple = 'gray75')     
    
def findEnvelope(): #get the max used Buildspace and position of the job
    x_coords = []
    y_coords = []    
    coord_max = [0,1]
    coord_min = [0,1]   

    for line in GCODE:        
       
        l = line.strip(line) # Strip all EOL characters for streaming         
        l = line.replace('X', '')
        l2 = l.replace('Y', '')        
        l2 = l2.split()     
        
        if len(l2) == 3:
            x = l2[1]
            x_coords.append(float(x))
            y = l2[2]
            y_coords.append(float(y))        

    x_coords.sort()
    y_coords.sort()
    coord_max[0] = max(x_coords) +50
    coord_max[1] = 350 - max(y_coords) #invertierte Buildplattform mit 0 unten links statt oben links
    coord_min[0] = min(x_coords) +50
    coord_min[1] = 350 - min(y_coords)  

    return coord_min, coord_max

def grblWrite(grbl):   
    #print("write1")
    GCODE.seek(0)                
    for line in GCODE:
        #print("write")
        l = line.strip(line) # Strip all EOL characters for streaming
        l = line.split(";",0)      
        grbl.write(str.encode(l[0]+ '\n')) # Send g-code block to grbl
        grbl_out = grbl.readline() # Wait for grbl response with carriage return        
        infoScreen(grbl_out.strip())

def grblClose(grbl):
    # Close file and serial port
    #f.close()
    try:
        grbl.close()
        print("closed")
        connect_ser.config(bg='grey')
    except:
        print("Connection still open")

#GUI Main
buttonsize_x = 5
buttonsize_y = 3
increments = 0

root = Tk()
root.title('touchCNC')
root.geometry('1024x600+0+0')

increments = IntVar()

left = Button(root, text="-X",  width = buttonsize_x, height = buttonsize_y, command = lambda:jogWrite(grbl, 'X', '-1', increments))
right = Button(root, text="+X",width = buttonsize_x, height = buttonsize_y,command = lambda:jogWrite(grbl, 'X', '1', increments))
up = Button(root, text="+Y", width = buttonsize_x, height = buttonsize_y,command = lambda:jogWrite(grbl, 'Y', '1', increments))
cancel = Button(root, text="cancel", width = buttonsize_x, height = buttonsize_y,bg = 'black', command = lambda:directWrite(grbl, '0x85' ))
down = Button(root, text="-Y",width = buttonsize_x, height = buttonsize_y,command = lambda:jogWrite(grbl, 'Y', '-1', increments))
z_up = Button(root, text="+Z",width = buttonsize_x, height = buttonsize_y,command = lambda:jogWrite(grbl, 'Z', '1', increments) )
z_down = Button(root, text="-Z",width = buttonsize_x, height = buttonsize_y,command = lambda:jogWrite(grbl, 'Z', '-1', increments))
zero_x = Button(root, text="zero X",width = buttonsize_x, height = buttonsize_y, command = lambda:zeroWrite(grbl,'G92', 'X' ))
zero_y = Button(root, text="zero Y",width = buttonsize_x, height = buttonsize_y, command = lambda:zeroWrite(grbl,'G92', 'Y' ))
zero_z = Button(root, text="zero Z",width = buttonsize_x, height = buttonsize_y, command = lambda:zeroWrite(grbl,'G92', 'Z' ))
zero_all =Button(root, text="zero All",width = buttonsize_x, height = buttonsize_y, command = lambda:zeroWrite(grbl,'G92', 'XYZ'))

connect_ser = Button(root, text="Cnnct",width = buttonsize_x, height = buttonsize_y, command = grblConnect2, bg = 'grey')
discon_ser = Button(root, text="Dsconct",width = buttonsize_x, height = buttonsize_y, command = lambda:grblClose(grbl))
unlock = Button(root, text="Unlock",width = buttonsize_x, height = buttonsize_y, command = lambda:directWrite(grbl, '$X'))
start = Button(root, text="START",width = buttonsize_x, height = buttonsize_y, bg = 'red', command = lambda: grblWrite(grbl))
stop = Button(root, text="STOP",width = buttonsize_x, height = buttonsize_y, bd= 3)
pause = Button(root, text="PAUSE",width = buttonsize_x, height = buttonsize_y, bg = '#007fff')
fopen = Button(root, text="GCODE",width = buttonsize_x , height = buttonsize_y, bg = 'grey', command = openGCODE)

spindle = Button(root, text="Spindle",width = buttonsize_x, height = buttonsize_y, bg = 'grey', command = lambda:latchWrite(grbl,'M3'))
coolant = Button(root, text="Coolant",width = buttonsize_x, height = buttonsize_y,command = lambda:latchWrite(grbl,'M8') )
tool = Button(root, text="Tool",width = buttonsize_x, height = buttonsize_y,command = lambda:latchWrite(grbl,'M6') )
macro = Button(root, text="Macro1",width = buttonsize_x, height = buttonsize_y,command = lambda:directWrite(grbl,' G90 G1 X10 Y10 Z50 F100') )

step_incr1 = Radiobutton(root, text= '0,1', value = 1 , variable = increments,width = buttonsize_x, height = buttonsize_y, indicatoron = 0 )
step_incr2 = Radiobutton(root, text= '1', value = 2 , variable = increments,width = buttonsize_x, height = buttonsize_y, indicatoron = 0 )
step_incr3 = Radiobutton(root, text= '10', value = 3 , variable = increments,width = buttonsize_x, height = buttonsize_y, indicatoron = 0 )
step_incr4 = Radiobutton(root, text= '100', value = 4 , variable = increments,width = buttonsize_x, height = buttonsize_y, indicatoron = 0 )
step_incr2.select()

terminal = Entry(root, width =8, text="GCODE")
terminal_send = Button(root, text="SEND",width = buttonsize_x, height = buttonsize_y, bd= 3, command = lambda: terminalWrite(grbl))
terminal_recv = Canvas(root, width = 200, height =400, bg = 'white')

show_ctrl_x_label = Label(root,text = "X")
show_ctrl_y_label = Label(root,text = "Y")
show_ctrl_z_label = Label(root,text = "Z")
show_ctrl_x =Label(root, text = "X ", width = 10, height = 2, bg ='white', relief = SUNKEN)
show_ctrl_y =Label(root, text = "Y ", width = 10, height = 2, bg ='white', relief = SUNKEN)
show_ctrl_z =Label(root, text = "Z ", width = 10, height = 2, bg ='white', relief = SUNKEN)

feed_control = Scale(root, orient = HORIZONTAL, length = 400, label = "Feedrate",tickinterval = 20)

#Milling Area and Gcode preview with grid generation

mill_table= Canvas(root, width= 400, height = 400, bg = 'grey')

mill_table.create_rectangle(50,50,350,350, fill ='white')
mill_table.create_text(200,25,text = 'Fräsbereich 300mm x 300mm')

for x in range(50,350,50):
    mill_table.create_text(x,400- x, text = x-50)

for x in range(0,400,50):
    for y in range(0,400,50):
        gitter_x = mill_table.create_line(x,0,x,400)
        gitter_y = mill_table.create_line(0,y,400,y)

left.grid(row=1, column=0, padx=3, pady=2)
cancel.grid(row=0, column=0, padx=3, pady=2)
right.grid(row=1, column=2,padx=3, pady=2)
up.grid(row=0, column=1, padx=3, pady=10)
down.grid(row=1, column=1,padx=3, pady=2)
z_up.grid(row=0, column=3,padx=10, pady=10)
z_down.grid(row=1, column=3,padx=10, pady=2)

step_incr2.select()

step_incr1.grid(row=2, column=0,padx=3, pady=10)
step_incr2.grid(row=2, column=1,padx=3, pady=10)
step_incr3.grid(row=2, column=2,padx=3, pady=10)
step_incr4.grid(row=2, column=3,padx=3, pady=10)

show_ctrl_x_label.grid(row=3, column=0,padx=3, pady=10)
show_ctrl_y_label.grid(row=4, column=0,padx=3, pady=10)
show_ctrl_z_label.grid(row=5, column=0,padx=3, pady=10)

show_ctrl_x.grid(row=3, column=1,padx=0, pady=0, columnspan =1)
show_ctrl_y.grid(row=4, column=1,padx=0, pady=0, columnspan =1)
show_ctrl_z.grid(row=5, column=1,padx=0, pady=0, columnspan =1)

zero_x.grid(row=6, column=0,padx=10, pady=10)
zero_y.grid(row=6, column=1,padx=10, pady=10)
zero_z.grid(row=6, column=2,padx=10, pady=10)
zero_all.grid(row=6, column=3,padx=10, pady=10)
connect_ser.grid(row=7, column=0,padx=10, pady=10)
discon_ser.grid(row=7, column=1,padx=10, pady=10)
unlock.grid(row=8, column=1,padx=10, pady=10)
start.grid(row=7, column=2,padx=10, pady=10)
stop.grid(row=7, column=3,padx=10, pady=10)
pause.grid(row=8, column=2,padx=10, pady=10, columnspan = 1)
fopen.grid(row=8, column=0,padx=10, pady=10)

spindle.grid(row=7, column=4,padx=1, pady=10)
coolant.grid(row=7, column=5,padx=1, pady=10)
tool.grid(row=7, column=6,padx=1, pady=10)
macro.grid(row=7, column=7,padx=1, pady=10)

terminal.grid(row = 7, column = 8, padx =2, pady =10)
terminal_send.grid(row = 7, column = 9, padx =2, pady =10)
terminal_recv.grid(row = 0, column = 8, padx =10, pady =10,rowspan = 7, columnspan =2)

feed_control.grid(row = 8, column = 4, columnspan =4)

mill_table.grid(row=0, column=4,padx=10, pady=10,columnspan = 4, rowspan = 7)

root.mainloop()

