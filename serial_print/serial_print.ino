/*
  Pedestrian Dead Reckoning Project
  Created: 12 October 2025
  Initial streaming of accelerometer, gyro and magnetometer data to the console
*/

#include "Arduino_BMI270_BMM150.h"

float linearX, linearY, linearZ;
float angularX, angularY, angularZ;
float magnetX, magnetY, magnetZ;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  //these lines may need to be removed later on
  // Serial.println("Started");
  // Serial.println("Timestamp, LinearX, LinearY, LinearZ, AngularX, AngularY, AngularZ, MagnetX, MagnetY, MagnetZ");
  
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

}

void loop() {
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(linearX, linearY, linearZ);
  }
  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(angularX, angularY, angularZ);
  }
  IMU.readMagneticField(magnetX, magnetY, magnetZ);
  
  Serial.print(millis()); Serial.print(", ");
  Serial.print(linearX); Serial.print(", "); Serial.print(linearY); Serial.print(", "); Serial.print(linearZ); Serial.print(", ");
  Serial.print(angularX); Serial.print(", "); Serial.print(angularY); Serial.print(", "); Serial.print(angularZ); Serial.print(", ");
  Serial.print(magnetX); Serial.print(", "); Serial.print(magnetY); Serial.print(", "); Serial.print(magnetZ); Serial.println("");
}
