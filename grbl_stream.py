import serial
import re
import time
import threading

RX_BUFFER_SIZE = 128
BAUD_RATE = 115200
ENABLE_STATUS_REPORTS = True
REPORT_INTERVAL = 1.0  # seconds

is_run = True  # Controls query timer

class GrblController:
    def __init__(self, device_file, verbose=True, settings_mode=False, check_mode=False):
        self.ser = serial.Serial(device_file, BAUD_RATE)
        self.verbose = verbose
        self.settings_mode = settings_mode
        self.check_mode = check_mode
        self.timerThread = None

    def open(self):
        self.ser.open()
        self.ser.flushInput()
        self.ser.flushOutput()
        time.sleep(2)
        self.ser.flushInput()
        if self.check_mode:
            self.set_check_mode()

    def close(self):
        self.ser.close()

    def set_check_mode(self):
        self.send_command("$C\n")
        while True:
            grbl_out = self.ser.readline().strip()
            if grbl_out.find('error') >= 0:
                print("REC:", grbl_out)
                print("  Failed to set Grbl check-mode. Aborting...")
                quit()
            elif grbl_out.find('ok') >= 0:
                if self.verbose:
                    print('REC:', grbl_out)
                break

    def send_command(self, command):
        self.ser.write((command + '\n').encode())

    def read_response(self):
        return self.ser.readline().strip()

    def send_gcode(self, gcode_file):
        l_count = 0
        error_count = 0
        start_time = time.time()
        self.start_status_report_timer()

        for line in gcode_file:
            l_count += 1
            l_block = line.strip()
            if self.settings_mode:
                self.send_command(l_block)
                while True:
                    grbl_out = self.read_response()
                    if grbl_out.find('ok') >= 0:
                        if self.verbose:
                            print("  REC<{}: \"{}\"".format(l_count, grbl_out))
                        break
                    elif grbl_out.find('error') >= 0:
                        if self.verbose:
                            print("  REC<{}: \"{}\"".format(l_count, grbl_out))
                        error_count += 1
                        break
                    else:
                        print("    MSG: \"{}\"".format(grbl_out))
            else:
                c_line = []
                for char in l_block:
                    c_line.append(len(char) + 1)
                    grbl_out = ''
                    while sum(c_line) >= RX_BUFFER_SIZE - 1 or self.ser.inWaiting():
                        out_temp = self.read_response()
                        if out_temp.find('ok') < 0 and out_temp.find('error') < 0:
                            print("    MSG: \"{}\"".format(out_temp))
                        else:
                            if out_temp.find('error') >= 0:
                                error_count += 1
                            del c_line[0]
                            if self.verbose:
                                print("  REC<{}: \"{}\"".format(l_count, out_temp))
                    self.send_command(char)
                    if self.verbose:
                        print("SND>{}: \"{}\"".format(l_count, char))

        while l_count > 0:
            out_temp = self.read_response()
            if out_temp.find('ok') < 0 and out_temp.find('error') < 0:
                print("    MSG: \"{}\"".format(out_temp))
            else:
                if out_temp.find('error') >= 0:
                    error_count += 1
                l_count -= 1
                del c_line[0]
                if self.verbose:
                    print("  REC<{}: \"{}\"".format(l_count, out_temp))

        self.stop_status_report_timer()
        end_time = time.time()
        is_run = False

        print("\nG-code streaming finished!")
        print("Time elapsed: {}\n".format(end_time - start_time))

        if self.check_mode:
            if error_count > 0:
                print("CHECK FAILED: {} errors found! See output for details.\n".format(error_count))
            else:
                print("CHECK PASSED: No errors found in g-code program.\n")
        else:
            print("WARNING: Wait until Grbl completes buffered g-code blocks before exiting.")

    def start_status_report_timer(self):
        if ENABLE_STATUS_REPORTS:
            self.timerThread = threading.Thread(target=self.periodic_timer)
            self.timerThread.daemon = True
            self.timerThread.start()

    def stop_status_report_timer(self):
        self.timerThread.join()

    def periodic_timer(self):
        while is_run:
            self.send_command('?')
            time.sleep(REPORT_INTERVAL)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Stream g-code file to grbl.')
    parser.add_argument('gcode_file', type=argparse.FileType('r'), help='g-code filename to be streamed')
    parser.add_argument('device_file', help='serial device path')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='suppress output text')
    parser.add_argument('-s', '--settings', action='store_true', default=False, help='settings write mode')
    parser.add_argument('-c', '--check', action='store_true', default=False, help='stream in check mode')
    args = parser.parse_args()

    grbl_controller = GrblController(args.device_file, not args.quiet, args.settings, args.check)
    grbl_controller.open()
    grbl_controller.send_gcode(args.gcode_file)
    grbl_controller.close()
