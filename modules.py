grbl = 0
port = None
i = 10
GCODE = 0
gcode_to_stream = []
countbuf = 0
writebuffer_byPass = []
writebuffer = []
readbuffer = []
AXIS = 'X'
states = {'M3': '0', 'M8': '0', 'M6': '0', 'G10': '0'}  # Spindle, Coolant, Toolchange
dict_GCODE = {'G': '0',
              'X': '0',
              'Y': '0',
              'Z': '0',
              'I': '0',
              'J': '0',
              'F': '0'
              }

# GUI Main
buttonsize_x = 5
buttonsize_y = 3
increments = 0
BORDER = 2
freetosend = 1

# GUI Color Scheme
attention = 'red'
loaded = 'green'
cooling = 'blue'
toolchange = 'yellow'
standard = '#17223B'
feed = '#283B67'


def grblConnect2():
    global grbl
    global port

    # Serial Connection
    locations = ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3',
                 '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3']

    for device in locations:
        try:
            # print([comport.device for comport in serial.tools.list_ports.comports()])
            print("Trying...", device)
            grbl = serial.Serial(port=device, baudrate=115200, timeout=.5)  # dsrdtr= True)
            port = device
            # grbl.open()
            # print(grbl.readline())
            grbl.write(str.encode("\r\n\r\n"))
            time.sleep(2)  # Wait for grbl to initialize
            grbl.flushInput()  # Flush startup text in serial input
            connect_ser.config(bg=loaded)
            # print("connected")

            break
        except:
            # print ("Failed to connect on",device)
            grbl = 0

    # Stream g-code to grbl
    # Stream GCODE from -https://onehossshay.wordpress.com/2011/08/26/grbl-a-simple-python-interface/-


def jogWrite(AXIS, CMD, scale):  # Schreiben von manuellen Positionierungsbefehlen
    global freetosend

    DECIMAL = [0.1, 1, 10, 100]
    scale = increments.get()
    MOVE = int(CMD) * DECIMAL[scale - 1]
    grbl_command = ('$J=G91' + 'G21' + AXIS + str(MOVE) + 'F1000')
    # print(grbl_command) $J=G91G21X10F185
    grbl_gcode_send.send_gcode(grbl, grbl_command)


def switchButtonState(button):  # Umschalter für Knopfstatus
    if button["state"] == DISABLED:
        button["state"] = NORMAL
    else:
        button["state"] = DISABLED


def directWrite(CMD):  # Direktes schreiben eines Befehls
    global freetosend
    # print(freetosend)
    grbl_command = CMD

    grbl_gcode_send.send_gcode(grbl, grbl_command)


def latchWrite(CMD):
    global states
    global freetosend
    if states[CMD] == '0':
        states[CMD] = '1'
        if CMD == 'M3':
            spindle.config(bg=attention)  # A31621
        if CMD == 'M6':
            tool.config(bg=toolchange)  # E0CA3C
        if CMD == 'G10':
            zero_all.config(bg=loaded)

    else:
        states[CMD] = '0'
        if CMD == 'M3':
            spindle.config(bg=loaded)  # A2D729
        if CMD == 'M6':
            tool.config(bg='grey')
        # if CMD == 'G10':
        #    zero_all.config(bg= attention)

    if CMD == 'M3':
        if states['M3'] == '1':
            grbl_command = 'M3 S1000'
        else:
            grbl_command = 'M3 S0'

    elif CMD == 'M8':
        if states['M8'] == '1':
            grbl_command = (CMD)
            coolant.config(bg=cooling)  # 1F7A8C
        else:
            grbl_command = 'M9'
            coolant.config(bg='grey')

    elif CMD == 'G10':
        grbl_command = 'G10 P0 L20 X0 Y0 Z0'

    else:
        grbl_command = (CMD)

        # grbl_command = (CMD * int(states[CMD]) )
    # print(grbl_command)
    # print(states)

    grbl_gcode_send.send_gcode(grbl, grbl_command)


def terminalWrite():  # Holt Zeichenstring von Editfeld und sendet es
    grbl_command = terminal.get()
    # print(grbl_command)

    grbl_gcode_send.send_gcode(grbl, grbl_command)


def infoScreen(data):  # Anzeigecanvas für GRBL Rückmeldungen
    global i
    terminalFrame = Frame(terminal_recv, bg='white')
    terminal_recv.create_window(10, i, window=terminalFrame, anchor='nw')
    Label(terminalFrame, text=data, font=('Calibri', 10), bg='white', fg='black').pack()
    i += 22
    if i >= 400:
        i = 10
        terminal_recv.delete("all")


def openGCODE():  # Dialog zur Gcode Auswahl und öffnen der Datei als GCODE Objekt
    global gcode_to_stream
    filetypes = (('GCODE', '*.nc'), ('All files', '*.*'))
    GCODE = fd.askopenfile(title='Open a file', initialdir='/home/thomas/Nextcloud/CAM/', filetypes=filetypes)

    if GCODE != 0:
        fopen.config(bg=loaded)
        extracted = extract_GCODE(GCODE)
        draw_GCODE(extracted)
        gcode_to_stream = GCODE

    else:
        fopen.config(bg='grey')

    # build_xy = findEnvelope() #Aufruf PLatz im Bauraum
    # mill_table.create_rectangle(build_xy[0],build_xy[1], fill = 'blue', stipple = 'gray75') # Zeichnen des Objekts im Bauraum


def extract_GCODE(gcode: list):  # Aufschlüsseln der enthaltenen Koordinaten in ein per Schlüssel zugängiges Dictionary

    list_dict_GCODE = []
    for line in gcode:
        l = line.split()  # Elemente trennen und in Liste konvertieren
        for i in range(0, len(l)):
            # print (l)
            if 'G' in l[i]:
                dict_GCODE['G'] = l[i].replace('G', '')  # Wert einfügen und gleichzeitig G CODE befehl entfernen
            if 'X' in l[i]:
                dict_GCODE['X'] = l[i].replace('X', '')
            if 'Y' in l[i]:
                dict_GCODE['Y'] = l[i].replace('Y', '')
            if 'Z' in l[i]:
                dict_GCODE['Z'] = l[i].replace('Z', '')
            if 'I' in l[i] and not 'ZMIN':
                dict_GCODE['I'] = l[i].replace('I', '')
            if 'J' in l[i]:
                dict_GCODE['J'] = l[i].replace('J', '')
            if 'F' in l[i] and not 'Fusion':
                dict_GCODE['F'] = l[i].replace('F', '')

                # print(dict_GCODE)
        list_dict_GCODE.append(
            dict_GCODE.copy())  # Copy notwendig da es sich nur um einen "Pointer" handelt der immer auf die zuletzt aktualisierte dict Zeile zeigt.
    print(list_dict_GCODE)

    return list_dict_GCODE


def draw_GCODE(glist):  # Zeichnen des GCodes zur Beurteilung des Bauraums

    for i in range(0, len(glist) - 1):
        x_y_current = 50 + float(glist[i]['X']), 350 - float(glist[i]['Y'])
        x_y_next = 50 + float(glist[i + 1]['X']), 350 - float(glist[i + 1]['Y'])

        mill_table.create_line(x_y_current, x_y_next)


def writeToFileLog(log):  # Log für Debugzwecke
    with open("log.txt", 'a') as out:
        out.write(log)


def displayPosition_request(grbl_pos):
    if grbl != 0:
        try:
            position = str(grbl_pos)
            # print (readbuffer)

            position = position.replace('Idle|', ',')
            position = position.replace('Run|', ',')
            position = position.replace('WPos:', '')
            position = position.replace('MPos:', '')
            position = position.replace('>', ',')
            position = position.replace('|', ',')
            position.strip()
            coordinates_list = position.split(',')
            # print(coordinates_list)
            show_ctrl_x.config(text=coordinates_list[1])
            show_ctrl_y.config(text=coordinates_list[2])
            show_ctrl_z.config(text=coordinates_list[3])

            mill_table.create_line(coordinates_list[1], coordinates_list[2], coordinates_list[1],
                                   coordinates_list[2] + 50, arrow=FIRST)

            # show_ctrl_x_w.config(text = coordinates_list[4])
            # show_ctrl_y_w.config(text = coordinates_list[5])
            # show_ctrl_z_w.config(text = coordinates_list[6])

        except:
            pass
            # print("Listerror")


    else:
        print("Serial Busy")
    # root.after(1000,displayPosition)


def displayPosition():
    global readbuffer
    if grbl != 0:
        try:
            position = str(readbuffer[2])
            # print (readbuffer)

            position = position.replace('Idle|', ',')
            position = position.replace('Run|', ',')
            position = position.replace('WPos:', '')
            position = position.replace('MPos:', '')
            position = position.replace('>', ',')
            position = position.replace('|', ',')
            position.strip()
            coordinates_list = position.split(',')
            # print(coordinates_list)
            show_ctrl_x.config(text=coordinates_list[1])
            show_ctrl_y.config(text=coordinates_list[2])
            show_ctrl_z.config(text=coordinates_list[3])

            mill_table.create_line(coordinates_list[1], coordinates_list[2], coordinates_list[1] + 10,
                                   coordinates_list[2] + 20)
            mill_table.create_line(coordinates_list[1], coordinates_list[2], coordinates_list[1] - 10,
                                   coordinates_list[2] + 20)
            mill_table.create_line(coordinates_list[1] - 10, coordinates_list[2] + 20, coordinates_list[1] + 10,
                                   coordinates_list[2] + 20)
            # show_ctrl_x_w.config(text = coordinates_list[4])
            # show_ctrl_y_w.config(text = coordinates_list[5])
            # show_ctrl_z_w.config(text = coordinates_list[6])

        except:
            pass
            # print("Listerror")

    else:
        print("Serial Busy")
    # root.after(1000,displayPosition)


def grblWrite():
    if gcode_to_stream != None:
        print("Stream", gcode_to_stream)
        grbl_gcode_send.send_gcode(grbl, gcode_to_stream)

    # fdbk = grbl_gcode_send.send_gcode(grbl, line)
    # print(fdbk)
    grbl_gcode_send.wait_for_buffer_empty()


def grblClose():
    # Close file and serial port
    # f.close()
    try:
        grbl.close()
        print("closed")
        connect_ser.config(bg='grey')
    except:
        print("Connection still open")