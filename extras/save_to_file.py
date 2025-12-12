"""
    Pedestrian Dead Reckoning
    25 October 2025
    Python script for fetching data from the Arduino to a file

    https://forum.arduino.cc/t/cant-use-pyserial-to-read-serial-data-from-arduino/98533?_gl=1*15mzcjg*_up*MQ..*_ga*NzY1MDU4OTI0LjE3NjEzNDMzMjQ.*_ga_NEXN8H46L5*czE3NjEzNDMzMjMkbzEkZzAkdDE3NjEzNDMzMjMkajYwJGwwJGg2OTQ1Mjc2ODE.
    https://stackoverflow.com/questions/50356224/serial-serialutil-serialexception-errno-16-could-not-open-port-errno-16-de
    https://stackoverflow.com/questions/49086627/how-do-i-close-serial-connection-when-i-interrupt-code
"""

import serial
from datetime import datetime

def read_serial(port, baudrate):
    
    # The Arduino IDE Serial Monitor has to be closed for this to work!
    # set timeout to 1 otherwise it writes almost every character in a new line
    with serial.Serial(port, baudrate, timeout=1) as ser, open(f"./data/{datetime.now().replace(microsecond=0)}_imu_data.csv", 'w') as file:
        try:
            file.write("Timestamp, LinearX, LinearY, LinearZ, AngularX, AngularY, AngularZ, MagnetX, MagnetY, MagnetZ\n")
            file.flush()
            while True:
                data = ser.readline().decode().strip()
                if data:
                    print(data)
                    file.write(data + "\n")
                    file.flush()
        except serial.SerialException as e:
            print(e)
        except KeyboardInterrupt:
            print("Program stopped!")

if __name__ == '__main__':
    read_serial('/dev/cu.usbmodem1101', 9600)