/*
  Pedestrian Dead Reckoning Project
  2 November 2025
  Initial BLE streaming of accelerometer, gyro and magnetometer data

  For now, the data is sectioned into 3 characteristics (acceleration, gyro, magnetometer)
  Each characteristic transmits an array of 3 numbers which corresponds to the X, Y, Z data from the sensors

  BLE MAC Address of the given arduino: d8:e6:79:3d:03:63
*/

#include "Arduino_BMI270_BMM150.h"
#include <ArduinoBLE.h>

#define BLE_MOTION_SERVICE_UUID "181A"
#define BLE_IMU_DATA_CHARACTERISTIC_UUID "1111" 

float linearX, linearY, linearZ;
float angularX, angularY, angularZ;
float magnetX, magnetY, magnetZ;

BLEService motionService(BLE_MOTION_SERVICE_UUID); 

// array of 3 floats + timestamp, 3*4 bytes from array + 1 byte from timestamp
BLECharacteristic imuCharacteristic(BLE_IMU_DATA_CHARACTERISTIC_UUID, BLERead | BLENotify, 40);

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("Started");
  
  // Initialize sensors
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  if (!BLE.begin()) {
    Serial.println("Failed to initialize BLE!");
    while (1);
  }

  BLE.setLocalName("Arduino Nano 33 Sense BLE");
  
  // Add services
  BLE.setAdvertisedService(motionService);
  motionService.addCharacteristic(imuCharacteristic);
  BLE.addService(motionService);

  // Write initial values
  float emptyData[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  imuCharacteristic.writeValue((uint8_t*)emptyData, sizeof(emptyData));
  BLE.advertise();

  Serial.print("Device Address: ");
  Serial.println(BLE.address());
}

void loop() {
  BLEDevice central = BLE.central();
  Serial.println("Looking for a central device...");
  delay(50);

  if (central) {
    Serial.println("* Connected to central device!");
    Serial.print("* Connected device MAC address: ");
    Serial.println(central.address());
    Serial.println(" ");

    while (central.connected()) {
      // measure
      if (IMU.accelerationAvailable()) {
        IMU.readAcceleration(linearX, linearY, linearZ);
      }
      if (IMU.gyroscopeAvailable()) {
        IMU.readGyroscope(angularX, angularY, angularZ);
      }
      IMU.readMagneticField(magnetX, magnetY, magnetZ);

      //gather + send
      uint8_t buffer[40];
      unsigned long timestamp = millis();
      
      float accelerationData[3] = {linearX, linearY, linearZ};
      float gyroData[3] = {angularX, angularY, angularZ};
      float magnetData[3] = {magnetX, magnetY, magnetZ}; 

      memcpy(buffer, &timestamp, 4);
      memcpy(buffer + 4, accelerationData, 12);
      memcpy(buffer + 16, gyroData, 12);
      memcpy(buffer + 28, magnetData, 12);
      imuCharacteristic.writeValue((uint8_t*)buffer, sizeof(buffer));
    }
    
    Serial.println("* Disconnected from central device!");
  }
}
