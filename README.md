# IMU Code for the PDR project

Code for transmitting IMU information via a serial or Bluetooth connection.

## Directories

- arduino: arduino code for serial and BLE
- central: code for the central device to connect arduinos
- data: output of the central
- extras: various scripts for testing, previous versions of programs...

## Steps

1. To run the code first upload the code to the Arduino from the arduino/ble_1_characteristic directory
2. Run the runner.py script in /central directory
3. Inside the "data" directory, IMU data will be found for each device

### Note

For some reason, if the Arduino was powered off, and then powered on, UPLOAD the code AGAIN otherwise it won't work.
