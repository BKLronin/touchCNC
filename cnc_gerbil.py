import logging
import time
from tkinter import Button, Label, Variable, IntVar, Canvas, Frame, Listbox, Entry, Radiobutton, Tk, constants, LEFT
from tkinter import filedialog as fd
import os
from gerbil.gerbil import Gerbil



class touchCNC:
    def __init__(self, root):
        self.root = root

        # GUI Main
        self.stick_var = None
        self.stick_var_disp = 'NSWE'
        self.buttonsize_x = 5
        self.buttonsize_y = 3
        self.buttonsize_y_s = 1
        self.pady_var = 3
        self.file_list = []
        self.list_items = Variable(value=self.file_list)
        self.increments = 0
        self.BORDER = 2
        self.feedspeed = None
        self.states = {'M3': '0', 'M8': '0', 'M6': '0', 'G10': '0', '32' :0}  # self.spindle, Coolant, Toolchange

        self.dict_GCODE = {'G': '0',
                      'X': '0',
                      'Y': '0',
                      'Z': '0',
                      'I': '0',
                      'J': '0',
                      'F': '0'
                      }

        # GUI Color Scheme
        self.attention = '#ED217C'
        self.special = '#EC058E'
        self.loaded = '#90E39A'
        self.cooling = '#86BBD8'
        self.toolchange = '#ADE25D'
        self.secondary = '#B9A44C'
        self.standard = '#6DB1BF'  #F5F5F5'
        self.feed = self.secondary
        self.transport = '#FA7921'

        self.increments = IntVar()
        self.movement = Frame(root, relief='ridge', bd=self.BORDER, padx=10, pady=10)

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

        self.zero_x = Button(root, text="zero X", width=self.buttonsize_x, height=self.buttonsize_y_s, command=lambda: self.directWrite('G10 P0 L20 X0'),
                        bd=self.BORDER, bg=self.secondary)
        self.zero_y = Button(root, text="zero Y", width=self.buttonsize_x, height=self.buttonsize_y_s, command=lambda: self.directWrite('G10 P0 L20 Y0'),
                        bd=self.BORDER, bg=self.secondary)
        self.zero_z = Button(root, text="zero Z", width=self.buttonsize_x, height=self.buttonsize_y_s, command=lambda: self.directWrite('G10 P0 L20 Z0'),
                        bd=self.BORDER, bg=self.secondary)
        self.zero_all = Button(root, text="zeroAll", width=self.buttonsize_x, height=self.buttonsize_y_s, command=lambda: self.latchWrite('G10'),
                          bd=self.BORDER, bg=self.special)

        self.setzero = Button(root, text="SetPOS", width=self.buttonsize_x, height=self.buttonsize_y_s,
                         command=lambda: self.directWrite('G28.1'), bd=self.BORDER, bg= self.standard)
        self.gozero = Button(root, text="GoPOS", width=self.buttonsize_x, height=self.buttonsize_y_s, command=lambda: self.directWrite('G28'),
                        bd=self.BORDER , bg= self.attention)

        self.connect_ser = Button(root, text="Cnnct", width=self.buttonsize_x, height=self.buttonsize_y,
                                  command=self.grblConnect2, bg=self.standard, bd=self.BORDER)
        self.discon_ser = Button(root, text="Dsconct", width=self.buttonsize_x, height=self.buttonsize_y, command= self.grblClose,
                            bd=self.BORDER, bg=self.standard)
        self.unlock = Button(root, text="Unlock", width=self.buttonsize_x, height=1, command=self.grblUnlock,
                        bd=self.BORDER)
        self.start = Button(root, text="START", width=self.buttonsize_x, height=self.buttonsize_y, bg=self.attention,
                       command=self.grblWrite, bd=self.BORDER)
        self.stop = Button(root, text="STOP", width=self.buttonsize_x, height=self.buttonsize_y, bd=self.BORDER, bg=self.transport,
                      command=self.grblStop)
        self.pause = Button(root, text="PAUSE", width=self.buttonsize_x, height=self.buttonsize_y, bd=self.BORDER, bg=self.transport,
                       command=self.grblPause)
        self.resume = Button(root, text="RESUME", width=self.buttonsize_x, height=self.buttonsize_y, bd=self.BORDER, bg=self.transport,
                        command=self.grblResume)

        self.fopen = Button(root, text="OPEN", width=self.buttonsize_x, height=self.buttonsize_y, bg=self.standard, fg='black',
                       command=self.openGCODE, bd=self.BORDER)

        self.fopendir = Button(root, text="DIR", width=self.buttonsize_x, height=self.buttonsize_y, bg=self.standard,
                            fg='black',
                            command=self.openDir, bd=self.BORDER)


        self.spindle = Button(root, text="Spindle", width=self.buttonsize_x, height=self.buttonsize_y, bg=self.standard,
                         command=lambda: self.latchWrite('M3'))
        self.coolant = Button(root, text="Coolant", width=self.buttonsize_x, height=self.buttonsize_y, bg=self.standard,
                         command=lambda: self.latchWrite('M8'))
        self.tool = Button(root, text="Tool", width=self.buttonsize_x, height=self.buttonsize_y, bg=self.standard, command=lambda: self.directWrite('G10'))
        self.macro = Button(root, text="Laser", width=self.buttonsize_x, height=self.buttonsize_y, bg=self.standard,
                       command=lambda: self.latchWrite('32')) #self.directWrite(' G91 G0 X10 Y10 Z50 F1000'))

        self.inc1 = Button(root, text="Inc 1%", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.feed_over_write(1),
                      bg=self.feed)
        self.inc10 = Button(root, text="Inc 10%", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.feed_over_write(10),
                       bg=self.feed)
        self.dec1 = Button(root, text="Dec 1%", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.feed_over_write(-1),
                      bg=self.feed)
        self.dec10 = Button(root, text="Dec 10%", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.feed_over_write(-10),
                       bg=self.feed)
        self.reset = Button(root, text="<RESET", width=self.buttonsize_x, height=self.buttonsize_y, command=lambda: self.feed_over_write(0),
                       bg=self.secondary)

        self.reboot = Button(root, text="REBOOT", width=self.buttonsize_x, height=self.buttonsize_y,
                        command=lambda: os.system('reboot'), bg=self.secondary)

        self.step_incr1 = Radiobutton(root, text='0,1', value=1, variable=self.increments, width=self.buttonsize_x,
                                 height=self.buttonsize_y, indicatoron=0, bg=self.secondary)
        self.step_incr2 = Radiobutton(root, text='1', value=2, variable=self.increments, width=self.buttonsize_x, height=self.buttonsize_y,
                                 indicatoron=0, bg=self.secondary)
        self.step_incr3 = Radiobutton(root, text='10', value=3, variable=self.increments, width=self.buttonsize_x, height=self.buttonsize_y,
                                 indicatoron=0, bg=self.secondary)
        self.step_incr4 = Radiobutton(root, text='100', value=4, variable=self.increments, width=self.buttonsize_x,
                                 height=self.buttonsize_y, indicatoron=0, bg=self.secondary)
        self.step_incr2.select()

        self.files = Listbox(root, bg='white', fg='black',font=("Arial", 16))
        self.terminal = Entry(root,  text="GCODE", fg= 'white')
        self.terminal_send = Button(root, text="SEND",  bd=3,command=lambda: self.directWrite(self.terminal.get()))

        self.terminal_recv = Label(root, bg='white', fg='black', text="Message Type")
        self.terminal_recv_content = Label(root, bg='white', fg='black', width= 35, wraplength=200, anchor=constants.W, justify=LEFT)

        self.terminal_recv_progress = Label(root, bg='white', fg='black', text="Progress")
        self.terminal_recv_feed = Label(root, bg='white', fg='black', text="Feed")

        self.show_ctrl_x_label = Label(root, text="X", fg= 'lightgrey')
        self.show_ctrl_y_label = Label(root, text="Y", fg= 'lightgrey')
        self.show_ctrl_z_label = Label(root, text="Z", fg= 'lightgrey')
        self.show_ctrl_x = Label(root, text="X_POS", width=8, height=2, bg='white', relief=constants.SUNKEN, fg='black')
        self.show_ctrl_y = Label(root, text="Y_POS", width=8, height=2, bg='white', relief=constants.SUNKEN, fg='black')
        self.show_ctrl_z = Label(root, text="Z_POS", width=8, height=2, bg='white', relief=constants.SUNKEN, fg='black')

        self.show_ctrl_x_w = Label(root, text="X_POS_W", width=8, height=2, bg='white', relief=constants.SUNKEN, fg='black')
        self.show_ctrl_y_w = Label(root, text="Y_POS_W", width=8, height=2, bg='white', relief=constants.SUNKEN, fg='black')
        self.show_ctrl_z_w = Label(root, text="Z_POS_W", width=8, height=2, bg='white', relief=constants.SUNKEN, fg='black')

        # self.feed_control = Scale(root, orient = HORIZONTAL, length = 400, label = "self.feedrate",tickinterval = 20)
        # Milling Area and Gcode preview with grid generation
        self.mill_table = Canvas(root, bg='grey')

        self.mill_table.create_rectangle(50, 50, 350, 350, fill='white')
        self.mill_table.create_text(200, 25, text='Fräsbereich 300mm x 300mm')

        for x in range(50, 350, 50):
            self.mill_table.create_text(x, 400 - x, text=x - 50)

        for x in range(0, 400, 50):
            for y in range(0, 400, 50):
                gitter_x = self.mill_table.create_line(x, 0, x, 400)
                gitter_y = self.mill_table.create_line(0, y, 400, y)

        self.movement.grid(row=0, column=0, columnspan=3, rowspan=1)
        self.left.grid(row=1, column=0, padx=3, pady=2, sticky=self.stick_var)
        self.right.grid(row=1, column=2, padx=3, pady=2, sticky=self.stick_var)
        self.up.grid(row=0, column=1, padx=3, pady=self.pady_var , sticky=self.stick_var)
        self.down.grid(row=1, column=1, padx=3, pady=2, sticky=self.stick_var)
        self.z_up.grid(row=0, column=3, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.z_down.grid(row=1, column=3, padx=10, pady=2, sticky=self.stick_var)

        self.step_incr2.select()

        self.step_incr1.grid(row=2, column=0, padx=3, pady=self.pady_var, sticky=self.stick_var)
        self.step_incr2.grid(row=2, column=1, padx=3, pady=self.pady_var, sticky=self.stick_var)
        self.step_incr3.grid(row=2, column=2, padx=3, pady=self.pady_var, sticky=self.stick_var)
        self.step_incr4.grid(row=2, column=3, padx=3, pady=self.pady_var, sticky=self.stick_var)

        self.show_ctrl_x_label.grid(row=3, column=0, padx=3, pady=self.pady_var, sticky=self.stick_var)
        self.show_ctrl_y_label.grid(row=4, column=0, padx=3, pady=self.pady_var, sticky=self.stick_var)
        self.show_ctrl_z_label.grid(row=5, column=0, padx=3, pady=self.pady_var, sticky=self.stick_var)

        self.show_ctrl_x.grid(row=3, column=1, padx=0, pady=0, columnspan=1, sticky=self.stick_var)
        self.show_ctrl_y.grid(row=4, column=1, padx=0, pady=0, columnspan=1, sticky=self.stick_var)
        self.show_ctrl_z.grid(row=5, column=1, padx=0, pady=0, columnspan=1, sticky=self.stick_var)
        self.show_ctrl_z.grid(row=5, column=1, padx=0, pady=0, columnspan=1, sticky=self.stick_var)

        self.show_ctrl_x_w.grid(row=3, column=2, padx=0, pady=0, columnspan=1, sticky=self.stick_var)
        self.show_ctrl_y_w.grid(row=4, column=2, padx=0, pady=0, columnspan=1, sticky=self.stick_var)
        self.show_ctrl_z_w.grid(row=5, column=2, padx=0, pady=0, columnspan=1, sticky=self.stick_var)

        self.zero_x.grid(row=3, column=3, sticky=self.stick_var)
        self.zero_y.grid(row=4, column=3, sticky=self.stick_var)
        self.zero_z.grid(row=5, column=3, sticky=self.stick_var)
        self.zero_all.grid(row=6, column=3, padx=10, pady=self.pady_var, sticky=self.stick_var)

        self.setzero.grid(row=6, column=0, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.gozero.grid(row=6, column=1, padx=10, pady=self.pady_var, sticky=self.stick_var)

        self.connect_ser.grid(row=7, column=0, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.discon_ser.grid(row=7, column=1, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.unlock.grid(row=8, column=9, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.start.grid(row=7, column=2, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.stop.grid(row=7, column=3, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.pause.grid(row=8, column=2, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.resume.grid(row=8, column=3, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.fopen.grid(row=8, column=0, padx=10, pady=self.pady_var, sticky=self.stick_var)
        self.fopendir.grid(row=8, column=1, padx=10, pady=self.pady_var, sticky=self.stick_var)

        self.spindle.grid(row=7, column=4, padx=1, pady=self.pady_var, sticky=self.stick_var)
        self.coolant.grid(row=7, column=5, padx=1, pady=self.pady_var, sticky=self.stick_var)
        self.tool.grid(row=7, column=6, padx=1, pady=self.pady_var, sticky=self.stick_var)
        self.macro.grid(row=7, column=7, padx=1, pady=self.pady_var, sticky=self.stick_var)

        self.dec10.grid(row=8, column=4, padx=1, pady=self.pady_var, sticky=self.stick_var)
        self.dec1.grid(row=8, column=5, padx=1, pady=self.pady_var, sticky=self.stick_var)
        self.inc1.grid(row=8, column=6, padx=1, pady=self.pady_var, sticky=self.stick_var)
        self.inc10.grid(row=8, column=7, padx=1, pady=self.pady_var, sticky=self.stick_var)

        self.reset.grid(row=8, column=8, padx=10, pady=self.pady_var, sticky='W')
        self.reboot.grid(row=8, column=9, padx=10, pady=self.pady_var)

        self.terminal.grid(row=7, column=8, padx=10, pady=self.pady_var, sticky='W')
        self.terminal_send.grid(row=7, column=9, padx=2, pady=self.pady_var)

        self.files.grid(row=0, column=8, padx=10, pady=self.pady_var, rowspan=3, columnspan=2, sticky=self.stick_var_disp)
        #self.terminal_recv.grid(row=3, column=8, padx=10, pady=self.pady_var, columnspan=2, sticky=self.stick_var)
        self.terminal_recv_content.grid(row=3, column=8, padx=10, pady=self.pady_var,rowspan=2, columnspan=2, sticky=self.stick_var_disp)
        self.terminal_recv_progress.grid(row=5, column=8, padx=10, pady=self.pady_var, columnspan=2, sticky=self.stick_var_disp)
        self.terminal_recv_feed.grid(row=6, column=8, padx=10, pady=self.pady_var, columnspan=2, sticky=self.stick_var_disp)
        self.mill_table.grid(row=0, column=4, padx=10, pady=self.pady_var, columnspan=4, rowspan=7, sticky=self.stick_var_disp)
        self.cursor_id = None

        # BlockedButtons
        self.blkbuttons = (self.up, self.down, self.left, self.right, self.z_up, self.z_down, self.zero_x, self.zero_y,
                           self.zero_z, self.zero_all, self.setzero, self.gozero, self.spindle)
        # Initialize the counter
        self.table = DrawonTable(self.mill_table)

    def on_zero_position(self, label, pos):
        #print("Updated", pos)
        label.config(text=pos)

    def gui_callback(self, eventstring, *data):
        args = []
        #print(data)
        for d in data:
            args.append(str(d))
        #print("GUI CALLBACK: event={} data={}".format(eventstring.ljust(30), ", ".join(args)))

        if eventstring == "on_stateupdate":
            #print("stateupdate", data)
            self.on_zero_position(self.show_ctrl_x, data[2][0])
            self.on_zero_position(self.show_ctrl_y, data[2][1])
            self.on_zero_position(self.show_ctrl_z, data[2][2])

            pos = [data[2][0], data[2][1]]
            #self.table.drawgridTable()
            self.table.setPos(pos)

            self.table.deleteCursor(self.cursor_id)
            self.cursor_id = self.table.drawToolCursor()

        elif eventstring == "on_hash_stateupdate":
            #print("args", type(data[0]))

            self.displayWorkPosition(data[0]["G28"])

        elif eventstring == "on_progress_percent":
            self.terminal_recv_progress.config(text=f"Job completion: {data[0]} %")

        elif eventstring == "on_feed_change":
            self.terminal_recv_feed.config(text=f"Feed: {data[0]} mm/min")
            self.feedspeed = data[0]

        elif eventstring == "on_rx_buffer_percent":
            pass

        elif eventstring == "on_gcode_parser_stateupdate":
            if len(data) > 9:
                self.feedspeed = data[10]

        elif eventstring == "on_read":
            if data[0] == '$32=1':
                self.macro.config(background=self.attention)

            elif data[0] == '$32=0':
                self.macro.config(background=self.loaded)

        #elif eventstring == "on_processed_command":
         #   pass

        elif eventstring == "on_line_sent":
            pass

        else:
            self.terminal_recv.config(text=eventstring)
            self.terminal_recv_content.config(text=data)

    import time
    import logging

    def grblConnect2(self, baudrate=115200, max_retries=5, retry_interval=3):
        retry_count = 0
        locations = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyUSB1', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3',
                     '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3']

        # Configure logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)

        if not grbl.connected:
            for device in locations:
                if retry_count < max_retries:
                    try:
                        logger.info(f"Attempting to connect to {device}")
                        grbl.cnect(path=device, baudrate=baudrate)

                        break

                    except Exception as e:
                        logger.error(f"Failed to connect to {device}: {e}")
                        self.terminal_recv_content.config(text=f"Failed to connect to {device}: {e}")
                        retry_count += 1
                        time.sleep(retry_interval)

                        logger.warning(f"Failed to connect after {max_retries} attempts.")

                    finally:
                        time.sleep(3)
                        grbl.setup_logging()
                        self.connect_ser.config(bg=self.loaded)
                        #rbl.request_settings()
                        logger.info(f"Connection successful to {device}")
                        self.terminal_recv_content.config(text=f"Connection successful to {device}")
                        grbl.connected = True
                        grbl.poll_start()
                        self.terminal_recv_content.config(text=f"State: {grbl.connected}")
                        #grbl.set_feed_override(True)

    def grblClose(self):
        grbl.softreset()
        grbl.disconnect()
        self.connect_ser.config(bg=self.secondary)

    def displayWorkPosition(self, pos: list):
        #print("update", pos)
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

    def directWrite(self, cmd):
        grbl.send_immediately(cmd)

    def feed_over_write(self, change: int):
        new_feed = self.feedspeed / 100 * change
        print(new_feed)
        grbl.request_feed(new_feed)

    def latchWrite(self, CMD):
        if self.states[CMD] == '0':
            self.states[CMD] = '1'
            self.update_button_color(CMD, True)
        else:
            self.states[CMD] = '0'
            self.update_button_color(CMD, False)

        grbl_command = self.get_grbl_command(CMD)
        grbl.send_immediately(grbl_command)

    def update_button_color(self, CMD, is_active):
        if CMD == 'M3':
            self.spindle.config(bg=self.attention if is_active else self.loaded)

        elif CMD == 'M6':
            self.tool.config(bg=self.toolchange if is_active else self.standard)

        elif CMD == 'G10':
            self.zero_all.config(bg=self.loaded if is_active else self.attention)

        elif CMD == '32':
            self.macro.config(bg=self.loaded if is_active else self.attention)

        elif CMD == 'M8':
            self.coolant.config(bg=self.cooling if is_active else self.standard)

    def get_grbl_command(self, CMD):
        if CMD == 'M3':
            return 'M3 S1000' if self.states['M3'] == '1' else 'M5'

        elif CMD == 'M8':
            return CMD if self.states[CMD] == '1' else 'M9'

        elif CMD == 'G10':
            return 'G10 P0 L20 X0 Y0 Z0'

        elif CMD == '32':
            return '$32=0' if self.states['32'] == '1' else '$32=1'
        else:
            return CMD
    def overrideCMD(self, cmd):
        pass
        #grbl.

    def openGCODE(self):
        filetypes = (('GCODE', '*.nc'), ('All files', '*.*'))
        if not self.file_list:
            GCODE = fd.askopenfilename(title='Open a file', initialdir='/home/thomas/Nextcloud/CAM/', filetypes=filetypes)
        else:
            GCODE = self.load_gcode_from_listbox()

        if GCODE:
            grbl.abort()
            grbl.job_new()
            self.fopen.config(bg=self.loaded)
            extracted = self.extract_GCODE(GCODE)
            draw = DrawonTable(self.mill_table)
            draw.drawgridTable()
            draw.setGCODE(extracted)
            draw.draw_GCODE(extracted)

            grbl.load_file(GCODE)

        else:
            self.fopen.config(bg=self.secondary)

    def get_filenames(self,base_path):
        filenames = []

        # Use os.listdir to get the list of files and directories in the base path
        entries = os.listdir(base_path)

        if entries:
            for entry in entries:
                # Use os.path.join to create the full path of the entry
                full_path = os.path.join(base_path, entry)

                # Check if the entry is a file (not a directory)
                if os.path.isfile(full_path):
                    # If it's a file, add it to the list of filenames
                    filenames.append(entry)
        else:
            filenames = ["Such Empty"]

        return filenames

    def openDir(self):
        self.file_list = []
        directory = fd.askdirectory(title='Open a Folder', initialdir='/home/thomas/Nextcloud/CAM/')
        #print(directory)
        allowed_extensions = {'nc', 'GCODE'}  # Use a set for efficient membership testing
        print(directory)

        if directory:
            filenames = self.get_filenames(directory)
            self.files.delete(0, constants.END)
            for file in filenames:
                # Check if the file has an allowed extension
                if any(file.lower().endswith(ext) for ext in allowed_extensions):
                    self.file_list.append(file)
                    self.files.insert("end", file)  # Add the filename to the Listbox
        else:
            print("Please select Folder")
            self.terminal_recv_content.config(text="Please select Folder")

        #print(self.file_list)
    def load_gcode_from_listbox(self):
        selected_indices = self.files.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            selected_item = self.files.get(selected_index)
            print("Selected item:", selected_item)
        else:
            print("No item selected")

        return selected_item


    def grblWrite(self):
        grbl.job_run()

    def grblStop(self):
        grbl.job_halt()

    def grblPause(self):
        grbl.hold()
        self.pause.config(bg='red')
    def grblResume(self):
        grbl.resume()
        self.pause.config(bg=self.transport)
    def grblUnlock(self):
        grbl.killalarm()

    def extract_GCODE(self, gcode_path: str):  # Aufschlüsseln der enthaltenen Koordinaten in ein per Schlüssel zugängiges Dictionary
        with open(gcode_path, 'r') as gcode:
            list_dict_GCODE = []
            for line in gcode:
                lines = line.split()  # Elemente trennen und in Liste konvertieren
                for command in lines:
                    # print (l)
                    if 'G' in command:
                        self.dict_GCODE['G'] = command.replace('G',
                                                       '')  # Wert einfügen und gleichzeitig G CODE befehl entfernen
                    if 'X' in command:
                        self.dict_GCODE['X'] = command.replace('X', '')
                    if 'Y' in command:
                        self.dict_GCODE['Y'] = command.replace('Y', '')
                    if 'Z' in command:
                        self.dict_GCODE['Z'] = command.replace('Z', '')
                    if 'I' in command and not 'ZMIN':
                        self.dict_GCODE['I'] = command.replace('I', '')
                    if 'J' in command:
                        self.dict_GCODE['J'] = command.replace('J', '')
                    if 'F' in command and not 'Fusion':
                        self.dict_GCODE['F'] = command.replace('F', '')

                        # print(dict_GCODE)
                list_dict_GCODE.append(
                    self.dict_GCODE.copy())  # Copy notwendig da es sich nur um einen "Pointer" handelt der immer auf die zuletzt aktualisierte dict Zeile zeigt.
            #print(list_dict_GCODE)

            return list_dict_GCODE



class DrawonTable:
    def __init__(self, mill_table: object):
        self.mill_table = mill_table
        self.gcode: list = None
        self.cursor_pos = None

    def setPos(self,pos):
        if pos != None:
            self.cursor_pos = pos

    def setGCODE(self, gcode: list):
        if gcode != None:
            self.gcode = gcode

    def clearTable(self):
        self.mill_table.delete('all')

    def drawToolCursor(self):
        id = self.mill_table.create_text(50 + float(self.cursor_pos[0]), 342 - float(self.cursor_pos[1]), text='V', fill = 'red', font=("Arial", 16))

        return id

    def deleteCursor(self, id):
        if id != None:
            #print("deleted")
            self.mill_table.delete(id)

    def draw_GCODE(self, glist):  # Zeichnen des GCodes zur Beurteilung des Bauraums

        self.drawgridTable()

        for i in range(0, len(glist) - 1):
            x_y_current = 50 + float(glist[i]['X']), 350 - float(glist[i]['Y'])
            x_y_next = 50 + float(glist[i + 1]['X']), 350 - float(glist[i + 1]['Y'])

            self.mill_table.create_line(x_y_current, x_y_next)

    def get_coordinates(self, point):
        x_str = point.get('X', '0')
        y_str = point.get('Y', '0')

        x = 50 + float(x_str[1:]) if x_str and x_str[0] == 'X' else 50
        y = 350 - float(y_str[1:]) if y_str and y_str[0] == 'Y' else 350

        return x, y

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


if __name__ == "__main__":
    root = Tk()
    root.title('touchCNC')
    root.geometry('1024x600+0+0')
    root.grid_propagate(True)
    root.resizable(False, False)  # 17203b
    root.attributes('-fullscreen', False)
    root.tk_setPalette(background='#4B4A67', foreground='black', activeBackground='#F99417',
                       activeForeground='lightgrey')


    app = touchCNC(root)
    grbl = Gerbil(app.gui_callback)
    grbl.hash_state_requested = True
    grbl.gcode_parser_state_requested = True

    root.mainloop()