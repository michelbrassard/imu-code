/*
  Pedestrian Dead Reckoning Project
  12 October 2025
  Initial BLE streaming of accelerometer, gyro and magnetometer data

  For now, the data is sectioned into 3 characteristics (acceleration, gyro, magnetometer)
  Each characteristic transmits an array of 3 numbers which corresponds to the X, Y, Z data from the sensors

  BLE MAC Address of the given arduino: d8:e6:79:3d:03:63
*/

#include "Arduino_BMI270_BMM150.h"
#include <ArduinoBLE.h>

// UUIDs are taken from this: https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/uuids/characteristic_uuids.yaml + GPT help
#define BLE_MOTION_SERVICE_UUID "181A"
#define BLE_ACCELERATION_CHARACTERISTIC_UUID "2D77"
#define BLE_GYRO_CHARACTERISTIC_UUID "2D76"
#define BLE_MAGNETOMETER_CHARACTERISTIC_UUID "2AA1"

float linearX, linearY, linearZ;
float angularX, angularY, angularZ;
float magnetX, magnetY, magnetZ;

BLEService motionService(BLE_MOTION_SERVICE_UUID); 

// array of 3 floats + timestamp, 3*4 bytes from array + 1 byte from timestamp
BLECharacteristic accelerationCharacteristic(BLE_ACCELERATION_CHARACTERISTIC_UUID, BLERead | BLENotify, 16); 
BLECharacteristic gyroscopeCharacteristic(BLE_GYRO_CHARACTERISTIC_UUID, BLERead | BLENotify, 16);
BLECharacteristic magnetometerCharacteristic(BLE_MAGNETOMETER_CHARACTERISTIC_UUID, BLERead | BLENotify, 16);

// additional descriptors used for readibility
BLEDescriptor accelerationDescription("2901", "Acceleration (m/s^2)");
BLEDescriptor gyroscopeDescription("2901", "Gyroscope (deg/s)");
BLEDescriptor magnetometerDescription("2901", "Magnetometer (µT)");

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

  accelerationCharacteristic.addDescriptor(accelerationDescription);
  gyroscopeCharacteristic.addDescriptor(gyroscopeDescription);
  magnetometerCharacteristic.addDescriptor(magnetometerDescription);
  
  // Add services
  BLE.setAdvertisedService(motionService);
  motionService.addCharacteristic(accelerationCharacteristic);
  motionService.addCharacteristic(gyroscopeCharacteristic);
  motionService.addCharacteristic(magnetometerCharacteristic);
  BLE.addService(motionService);

  // Write initial values
  float emptyData[4] = {0, 0, 0, 0};
  accelerationCharacteristic.writeValue((uint8_t*)emptyData, sizeof(emptyData));
  gyroscopeCharacteristic.writeValue((uint8_t*)emptyData, sizeof(emptyData));
  magnetometerCharacteristic.writeValue((uint8_t*)emptyData, sizeof(emptyData));
  BLE.advertise();

  Serial.print("Device BLE MAC: ");
  Serial.println(BLE.address());
}

void loop() {
  BLEDevice central = BLE.central();
  Serial.println("Looking for a central device...");
  delay(500);

  if (central) {
    Serial.println("* Connected to central device!");
    Serial.print("* Device MAC address: ");
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
      uint8_t buffer[16];
      unsigned long timestamp = millis();
      
      float accelerationData[3] = {linearX, linearY, linearZ};
      memcpy(buffer, &timestamp, 4);
      memcpy(buffer + 4, accelerationData, 12);
      accelerationCharacteristic.writeValue((uint8_t*)buffer, sizeof(buffer));

      float gyroData[3] = {angularX, angularY, angularZ};
      memcpy(buffer, &timestamp, 4);
      memcpy(buffer + 4, gyroData, 12);
      gyroscopeCharacteristic.writeValue((uint8_t*)buffer, sizeof(buffer));

      float magnetData[3] = {magnetX, magnetY, magnetZ}; 
      memcpy(buffer, &timestamp, 4);
      memcpy(buffer + 4, magnetData, 12);
      magnetometerCharacteristic.writeValue((uint8_t*)buffer, sizeof(buffer));
    }
    
    Serial.println("* Disconnected from central device!");
  }
}
