import serial
import time

# Set your port and baud rate
SERIAL_PORT = '/dev/cu.usbmodem1101'  # or 'COM3' on Windows
BAUD_RATE = 9600
FILENAME = 'arduino_output.txt'

with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser, open(FILENAME, 'w') as f:
    print(f"Saving Arduino data from {SERIAL_PORT} to {FILENAME}...\n")
    try:
        while True:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print(line)
                f.write(line + '\n')
                f.flush()
    except KeyboardInterrupt:
        print("\nStopped logging.")


