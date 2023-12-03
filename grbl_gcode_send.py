import serial
import time

# Define the serial port and baud rate for communication
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Function to send G-code commands
def send_gcode(ser, command):
    # Split the command into chunks of 120 characters or less
    chunks = [command[i:i + 120] for i in range(0, len(command), 120)]

    for chunk in chunks:
        ser.write((chunk + '\n').encode())
        response = ser.readline().decode().strip()
        if response != 'ok':
            # Handle errors or unexpected responses here
            print(f"GRBL response: {response}")

# Function to wait until the buffer is empty
def wait_for_buffer_empty():
    while True:
        status = send_gcode('?')
        if status.startswith('<Idle'):
            break
        time.sleep(0.1)

if __name__ == "__main__":

    # Your G-code commands
    gcode_commands = [
        'G21',          # Set units to millimeters
        'G90',          # Set to absolute positioning
        'G1 X10 Y10 F100',  # Move to X10 Y10 at a feed rate of 100 mm/min
        'G1 X20 Y20 F100',
    ]

    try:
        # Initialize communication

        #ser.open()
        ser.flushInput()
        ser.flushOutput()

        # Send G-code commands
        for command in gcode_commands:
            send_gcode(command)

        # Wait for the buffer to empty
        wait_for_buffer_empty()

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        ser.close()