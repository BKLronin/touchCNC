import serial
import time
from tkinter import *
import serial.tools.list_ports
from tkinter import filedialog as fd
import os
import threading
from gerbil.gerbil import Gerbil



class touchCNC:
    def __init__(self, root):
        self.root = root

        # GUI Main
        self.buttonsize_x = 5
        self.buttonsize_y = 3
        self.increments = 0
        self.BORDER = 2
        self.states = {'M3': '0', 'M8': '0', 'M6': '0', 'G10': '0'}  # self.spindle, Coolant, Toolchange

        self.dict_GCODE = {'G': '0',
                      'X': '0',
                      'Y': '0',
                      'Z': '0',
                      'I': '0',
                      'J': '0',
                      'F': '0'
                      }

        # GUI Color Scheme
        self.attention = 'red'
        self.loaded = 'green'
        self.cooling = 'blue'
        self.toolchange = 'yellow'
        self.standard = '#17223B'
        self.feed = '#283B67'

        self.increments = IntVar()
        self.movement = Frame(root, relief='ridge', bd=self.BORDER)
        self.left = Button(root, text="-X", width=self.buttonsize_x, height=self.buttonsize_y,
                      command=lambda: self.jogWrite('X', '-1', self.increments), bd=self.BORDER, bg=self.standard)
        self.right = Button(root, text="+X", width=self.buttonsize_x, height=self.buttonsize_y,
                       command=lambda: self.jogWrite('X', '1', self.increments), bd=self.BORDER, bg=self.standard)
        self.up = Button(root, text="+Y", width=self.buttonsize_x, height=self.buttonsize_y,
                    command=lambda: self.jogWrite('Y', '1', self.increments), bd=self.BORDER, bg=self.standard)
        self.down = Button(root, text="-Y", width=self.buttonsize_x, height=self.buttonsize_y,
                      command=lambda: self.jogWrite('Y', '-1', self.increments), bd=self.BORDER, bg=self.standard)
        self.z_up = Button(root, text="+Z", width=self.buttonsize_x, height=self.buttonsize_y,
                      command=lambda: self.jogWrite('Z', '1', self.increments), bd=self.BORDER, bg=self.standard)
        self.z_down = Button(root, text="-Z", width=self.buttonsize_x, height=self.buttonsize_y,
                        command=lambda: self.jogWrite('Z', '-1', self.increments), bd=self.BORDER, bg=self.standard)

        self.zero_x = Button(root, text="zero X", width=self.buttonsize_x, height=1, command=lambda: self.directWrite('G10 P0 L20 X0'),
                        bd=self.BORDER)
        self.zero_y = Button(root, text="zero Y", width=self.buttonsize_x, height=1, command=lambda: self.directWrite('G10 P0 L20 Y0'),
                        bd=self.BORDER)
        self.zero_z = Button(root, text="zero Z", width=self.buttonsize_x, height=1, command=lambda: self.directWrite('G10 P0 L20 Z0'),
                        bd=self.BORDER)
        self.zero_all = Button(root, text="zeroAll", width=self.buttonsize_x, height=3, command=lambda: self.latchWrite('G10'),
                          bd=self.BORDER, bg='magenta')

        self.setzero = Button(root, text="SetPOS", width=self.buttonsize_x, height=self.buttonsize_y,
                         command=lambda: self.directWrite('G28.1'), bd=self.BORDER)
        self.gozero = Button(root, text="GoPOS", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.directWrite('G28'),
                        bd=self.BORDER)

        self.connect_ser = Button(root, text="Cnnct", width=self.buttonsize_x, height=self.buttonsize_y,
                                  command=self.grblConnect2, bg='grey', bd=self.BORDER)
        self.discon_ser = Button(root, text="Dsconct", width=self.buttonsize_x, height=self.buttonsize_y, command= self.grblClose,
                            bd=self.BORDER)
        self.unlock = Button(root, text="Unlock", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.directWrite('$X'),
                        bd=self.BORDER)
        self.start = Button(root, text="START", width=self.buttonsize_x, height=self.buttonsize_y, bg=self.attention,
                       command=self.grblWrite, bd=self.BORDER)
        self.stop = Button(root, text="STOP", width=self.buttonsize_x, height=self.buttonsize_y, bd=self.BORDER,
                      command=self.grblStop)
        self.pause = Button(root, text="PAUSE", width=self.buttonsize_x, height=self.buttonsize_y, bg=self.cooling, bd=self.BORDER,
                       command=self.grblPause)
        self.resume = Button(root, text="RESUME", width=self.buttonsize_x, height=self.buttonsize_y, bd=self.BORDER,
                        command=lambda: self.directWrite('~'))

        self.fopen = Button(root, text="GCODE", width=self.buttonsize_x, height=self.buttonsize_y, bg='grey', fg='black',
                       command=self.openGCODE, bd=self.BORDER)

        self.spindle = Button(root, text="Spindle", width=self.buttonsize_x, height=self.buttonsize_y,
                         command=lambda: self.latchWrite('M3'))
        self.coolant = Button(root, text="Coolant", width=self.buttonsize_x, height=self.buttonsize_y,
                         command=lambda: self.latchWrite('M8'))
        self.tool = Button(root, text="Tool", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.latchWrite('M6'))
        self.macro = Button(root, text="Macro1", width=self.buttonsize_x, height=self.buttonsize_y,
                       command=lambda: self.directWrite(' G91 G0 X10 Y10 Z50 F1000'))

        self.inc1 = Button(root, text="Inc 1%", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.directWrite('‘'),
                      bg=self.feed)
        self.inc10 = Button(root, text="Inc 10%", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.directWrite('“'),
                       bg=self.feed)
        self.dec1 = Button(root, text="Dec 1%", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.directWrite('”'),
                      bg=self.feed)
        self.dec10 = Button(root, text="Dec 10%", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.directWrite('’'),
                       bg=self.feed)
        self.reset = Button(root, text="<RESET", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.directWrite(''),
                       bg='grey')

        self.reboot = Button(root, text="REBOOT", width=self.buttonsize_x, height=self.buttonsize_y,
                        command=lambda: os.system('reboot'), bg='grey')

        self.step_incr1 = Radiobutton(root, text='0,1', value=1, variable=self.increments, width=self.buttonsize_x,
                                 height=self.buttonsize_y, indicatoron=0)
        self.step_incr2 = Radiobutton(root, text='1', value=2, variable=self.increments, width=self.buttonsize_x, height=self.buttonsize_y,
                                 indicatoron=0)
        self.step_incr3 = Radiobutton(root, text='10', value=3, variable=self.increments, width=self.buttonsize_x, height=self.buttonsize_y,
                                 indicatoron=0)
        self.step_incr4 = Radiobutton(root, text='100', value=4, variable=self.increments, width=self.buttonsize_x,
                                 height=self.buttonsize_y, indicatoron=0)
        self.step_incr2.select()

        self.terminal = Entry(root, width=8, text="GCODE")
        self.terminal_send = Button(root, text="SEND", width=self.buttonsize_x, height=self.buttonsize_y, bd=3,
                               command=lambda: terminalWrite())
        self.terminal_recv = Canvas(root, width=200, height=400, bg='white')

        self.show_ctrl_x_label = Label(root, text="X")
        self.show_ctrl_y_label = Label(root, text="Y")
        self.show_ctrl_z_label = Label(root, text="Z")
        self.show_ctrl_x = Label(root, text="X_POS", width=8, height=2, bg='white', relief=SUNKEN, fg='black')
        self.show_ctrl_y = Label(root, text="Y_POS", width=8, height=2, bg='white', relief=SUNKEN, fg='black')
        self.show_ctrl_z = Label(root, text="Z_POS", width=8, height=2, bg='white', relief=SUNKEN, fg='black')

        self.show_ctrl_x_w = Label(root, text="X_POS_W", width=8, height=2, bg='white', relief=SUNKEN, fg='black')
        self.show_ctrl_y_w = Label(root, text="Y_POS_W", width=8, height=2, bg='white', relief=SUNKEN, fg='black')
        self.show_ctrl_z_w = Label(root, text="Z_POS_W", width=8, height=2, bg='white', relief=SUNKEN, fg='black')

        # self.feed_control = Scale(root, orient = HORIZONTAL, length = 400, label = "self.feedrate",tickinterval = 20)

        # Milling Area and Gcode preview with grid generation

        self.mill_table = Canvas(root, width=400, height=400, bg='grey')

        self.mill_table.create_rectangle(50, 50, 350, 350, fill='white')
        self.mill_table.create_text(200, 25, text='Fräsbereich 300mm x 300mm')

        for x in range(50, 350, 50):
            self.mill_table.create_text(x, 400 - x, text=x - 50)

        for x in range(0, 400, 50):
            for y in range(0, 400, 50):
                gitter_x = self.mill_table.create_line(x, 0, x, 400)
                gitter_y = self.mill_table.create_line(0, y, 400, y)

        self.mill_table_draw_layer =Canvas(root, width=400, height=400, bg='grey')

        self.movement.grid(row=0, column=0, columnspan=3, rowspan=1)
        self.left.grid(row=1, column=0, padx=3, pady=2)
        self.right.grid(row=1, column=2, padx=3, pady=2)
        self.up.grid(row=0, column=1, padx=3, pady=10)
        self.down.grid(row=1, column=1, padx=3, pady=2)
        self.z_up.grid(row=0, column=3, padx=10, pady=10)
        self.z_down.grid(row=1, column=3, padx=10, pady=2)

        self.step_incr2.select()

        self.step_incr1.grid(row=2, column=0, padx=3, pady=10)
        self.step_incr2.grid(row=2, column=1, padx=3, pady=10)
        self.step_incr3.grid(row=2, column=2, padx=3, pady=10)
        self.step_incr4.grid(row=2, column=3, padx=3, pady=10)

        self.show_ctrl_x_label.grid(row=3, column=0, padx=3, pady=10)
        self.show_ctrl_y_label.grid(row=4, column=0, padx=3, pady=10)
        self.show_ctrl_z_label.grid(row=5, column=0, padx=3, pady=10)

        self.show_ctrl_x.grid(row=3, column=1, padx=0, pady=0, columnspan=1)
        self.show_ctrl_y.grid(row=4, column=1, padx=0, pady=0, columnspan=1)
        self.show_ctrl_z.grid(row=5, column=1, padx=0, pady=0, columnspan=1)

        self.show_ctrl_x_w.grid(row=3, column=2, padx=0, pady=0, columnspan=1)
        self.show_ctrl_y_w.grid(row=4, column=2, padx=0, pady=0, columnspan=1)
        self.show_ctrl_z_w.grid(row=5, column=2, padx=0, pady=0, columnspan=1)

        self.zero_x.grid(row=3, column=3)
        self.zero_y.grid(row=4, column=3)
        self.zero_z.grid(row=5, column=3)
        self.zero_all.grid(row=6, column=3, padx=10, pady=10)

        self.setzero.grid(row=6, column=0, padx=10, pady=10)
        self.gozero.grid(row=6, column=1, padx=10, pady=10)

        self.connect_ser.grid(row=7, column=0, padx=10, pady=10)
        self.discon_ser.grid(row=7, column=1, padx=10, pady=10)
        self.unlock.grid(row=8, column=1, padx=10, pady=10)
        self.start.grid(row=7, column=2, padx=10, pady=10)
        self.stop.grid(row=7, column=3, padx=10, pady=10)
        self.pause.grid(row=8, column=2, padx=10, pady=10)
        self.resume.grid(row=8, column=3, padx=10, pady=10)
        self.fopen.grid(row=8, column=0, padx=10, pady=10)

        self.spindle.grid(row=7, column=4, padx=1, pady=10)
        self.coolant.grid(row=7, column=5, padx=1, pady=10)
        self.tool.grid(row=7, column=6, padx=1, pady=10)
        self.macro.grid(row=7, column=7, padx=1, pady=10)

        self.dec10.grid(row=8, column=4, padx=1, pady=10)
        self.dec1.grid(row=8, column=5, padx=1, pady=10)
        self.inc1.grid(row=8, column=6, padx=1, pady=10)
        self.inc10.grid(row=8, column=7, padx=1, pady=10)

        self.reset.grid(row=8, column=8, padx=1, pady=10)
        self.reboot.grid(row=8, column=9, padx=1, pady=10)

        self.terminal.grid(row=7, column=8, padx=2, pady=10)
        self.terminal_send.grid(row=7, column=9, padx=2, pady=10)
        self.terminal_recv.grid(row=0, column=8, padx=10, pady=10, rowspan=7, columnspan=2)

        # self.feed_control.grid(row = 8, column = 4, columnspan =4)

        self.mill_table.grid(row=0, column=4, padx=10, pady=10, columnspan=4, rowspan=7)
        #self.mill_table_draw_layer.grid(row=0, column=4, padx=10, pady=10, columnspan=4, rowspan=7)

        self.cursor_id = None

        # sendGRBL()

        # BlockedButtons
        self.blkbuttons = (self.up, self.down, self.left, self.right, self.z_up, self.z_down, self.zero_x, self.zero_y,
                           self.zero_z, self.zero_all, self.setzero, self.gozero, self.spindle)
        # Initialize the counter
        self.table = DrawWorkingtable(self.mill_table)

    def on_zero_position(self, label, pos):
        print("Updated", pos)
        label.config(text=pos)

    def gui_callback(self, eventstring, *data):
        args = []
        print(data)
        for d in data:
            args.append(str(d))
        print("GUI CALLBACK: event={} data={}".format(eventstring.ljust(30), ", ".join(args)))

        if eventstring == "on_stateupdate":
            print("stateupdate", data)
            self.on_zero_position(self.show_ctrl_x, data[2][0])
            self.on_zero_position(self.show_ctrl_y, data[2][1])
            self.on_zero_position(self.show_ctrl_z, data[2][2])

            pos = [data[2][0], data[2][1]]
            #self.table.drawgridTable()
            self.table.setPos(pos)

            self.table.deleteCursor(self.cursor_id)
            self.cursor_id = self.table.drawToolCursor()


        if eventstring == "on_hash_stateupdate":
            print("args", type(data[0]))

            self.displayWorkPosition(data[0]["G28"])

    def grblConnect2(self):
        grbl.cnect("/dev/ttyUSB0", 115200)  # or /dev/ttyACM0
        time.sleep(2)
        if grbl.connected:
            grbl.poll_start()
        else:
            print("wtf -couldnt start thread")

    def displayWorkPosition(self, pos: list):
        print("update", pos)
        self.show_ctrl_x_w.config(text = pos[0])
        self.show_ctrl_y_w.config(text = pos[1])
        self.show_ctrl_z_w.config(text = pos[2])
        #self.root.after(1000, self.getPosition)

    def jogWrite(self, axis, cmd, scale):
        DECIMAL = [0.1, 1, 10, 100]
        scale = self.increments.get()
        MOVE = int(cmd) * DECIMAL[scale - 1]
        grbl_command = ('$J=G91' + 'G21' + axis + str(MOVE) + 'F1000')
        # print(grbl_command) $J=G91G21X10F185

        grbl.send_immediately(grbl_command)

    def directWrite(self,cmd):
        grbl.send_immediately(cmd)

    def latchWrite(self, CMD):        
        
        if self.states[CMD] == '0':
            self.states[CMD] = '1'
            if CMD == 'M3':
                self.spindle.config(bg=self.attention)  # A31621
            if CMD == 'M6':
                self.tool.config(bg=self.toolchange)  # E0CA3C
            if CMD == 'G10':
                self.zero_all.config(bg=self.loaded)

        else:
            self.states[CMD] = '0'
            if CMD == 'M3':
                self.spindle.config(bg=self.loaded)  # A2D729
            if CMD == 'M6':
                self.tool.config(bg='grey')
            # if CMD == 'G10':
            #    zero_all.config(bg= attention)

        if CMD == 'M3':
            if self.states['M3'] == '1':
                grbl_command = 'M3 S1000'
            else:
                grbl_command = 'M3 S0'

        elif CMD == 'M8':
            if self.states['M8'] == '1':
                grbl_command = (CMD)
                self.coolant.config(bg=self.cooling)  # 1F7A8C
            else:
                grbl_command = 'M9'
                self.coolant.config(bg='grey')

        elif CMD == 'G10':
            grbl_command = 'G10 P0 L20 X0 Y0 Z0'

        else:
            grbl_command = (CMD)

            # grbl_command = (CMD * int(self.[CMD]) )   
        # print(grbl_command)
        # print(self.)

        grbl.send_immediately(grbl_command)

    def overrideCMD(self,cmd):
        pass
        #grbl.

    def openGCODE(self):
        filetypes = (('GCODE', '*.nc'), ('All files', '*.*'))
        GCODE = fd.askopenfilename(title='Open a file', initialdir='/home/thomas/Nextcloud/CAM/', filetypes=filetypes)

        if GCODE != 0:
            self.fopen.config(bg=self.loaded)
            extracted = self.extract_GCODE(GCODE)
            draw = DrawWorkingtable(self.mill_table)
            draw.drawgridTable()
            draw.setGCODE(extracted)
            draw.draw_GCODE()


            grbl.load_file(GCODE)

        else:
            self.fopen.config(bg='grey')

    def grblWrite(self):
        grbl.job_run()
    def grblStop(self):
        grbl.abort()

    def grblPause(self):
        grbl.hold()

    def extract_GCODE(self, gcode_path: str):  # Aufschlüsseln der enthaltenen Koordinaten in ein per Schlüssel zugängiges Dictionary
        with open(gcode_path, 'r') as gcode:
            list_dict_GCODE = []
            for line in gcode:
                l = line.split()  # Elemente trennen und in Liste konvertieren
                for i in range(0, len(l)):
                    # print (l)
                    if 'G' in l[i]:
                        self.dict_GCODE['G'] = l[i].replace('G',
                                                       '')  # Wert einfügen und gleichzeitig G CODE befehl entfernen
                    if 'X' in l[i]:
                        self.dict_GCODE['X'] = l[i].replace('X', '')
                    if 'Y' in l[i]:
                        self.dict_GCODE['Y'] = l[i].replace('Y', '')
                    if 'Z' in l[i]:
                        self.dict_GCODE['Z'] = l[i].replace('Z', '')
                    if 'I' in l[i] and not 'ZMIN':
                        self.dict_GCODE['I'] = l[i].replace('I', '')
                    if 'J' in l[i]:
                        self.dict_GCODE['J'] = l[i].replace('J', '')
                    if 'F' in l[i] and not 'Fusion':
                        self.dict_GCODE['F'] = l[i].replace('F', '')

                        # print(dict_GCODE)
                list_dict_GCODE.append(
                    self.dict_GCODE.copy())  # Copy notwendig da es sich nur um einen "Pointer" handelt der immer auf die zuletzt aktualisierte dict Zeile zeigt.
            print(list_dict_GCODE)

            return list_dict_GCODE

    def grblClose(self):
        grbl.disconnect()

class DrawWorkingtable:
    def __init__(self, mill_table: object):
        self.mill_table = mill_table
        self.gcode: list = None
        self.cursor_pos = None

    def setPos(self,pos):
        if pos != None:
            self.cursor_pos = pos

    def setGCODE(self, gcode:list):
        if gcode != None:
            self.gcode = gcode

    def clearTable(self):
        self.mill_table.delete('all')

    def drawToolCursor(self):
        id = self.mill_table.create_text(50 + float(self.cursor_pos[0]), 350 - float(self.cursor_pos[1]), text='V', fill = 'red')

        return id

    def deleteCursor(self, id):
        if id != None:
            print("deleted")
            self.mill_table.delete(id)

    def draw_GCODE(self):  # Zeichnen des GCodes zur Beurteilung des Bauraums
        glist = self.gcode
        self.drawgridTable()

        for i in range(0, len(glist) - 1):
            x_y_current = 50 + float(glist[i]['X']), 350 - float(glist[i]['Y'])
            x_y_next = 50 + float(glist[i + 1]['X']), 350 - float(glist[i + 1]['Y'])

            self.mill_table.create_line(x_y_current, x_y_next)

    def drawgridTable(self):
        self.mill_table.delete('all')

        self.mill_table.create_rectangle(50, 50, 350, 350, fill='white')
        self.mill_table.create_text(200, 25, text='Fräsbereich 300mm x 300mm')

        for x in range(50, 350, 50):
            self.mill_table.create_text(x, 400 - x, text=x - 50)

        for x in range(0, 400, 50):
            for y in range(0, 400, 50):
                gitter_x = self.mill_table.create_line(x, 0, x, 400)
                gitter_y = self.mill_table.create_line(0, y, 400, y)


    print("test")

if __name__ == "__main__":
    root = Tk()
    root.title('touchCNC')
    root.geometry('1024x600+0+0')
    root.geometry('1024x600+0+0')
    root.resizable(False, False)  # 17203b
    root.attributes('-fullscreen', False)
    root.tk_setPalette(background='#11192C', foreground='white', activeBackground='#283867',
                       activeForeground='white')

    app = touchCNC(root)
    grbl = Gerbil(app.gui_callback)
    grbl.setup_logging()
    grbl.hash_state_requested = True
    grbl.gcode_parser_state_requested = True

    root.mainloop()