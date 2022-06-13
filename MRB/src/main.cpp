#include <Arduino.h>
#include <Servo.h>
#include "Definitions.hpp"

// #define DEBUG

struct ServoStanden{
  int servo1;
  int servo2;
  int servo3;
};


void SerialFlush(){
  while(Serial.available()){
    Serial.read();
  }
}

ServoStanden GetServoStandenFromSerial(){
  ServoStanden standen;
  standen.servo1 = Serial.parseInt();
  standen.servo2 = Serial.parseInt();
  standen.servo3 = Serial.parseInt();
  return standen;
}

Servo s1;
Servo s2;
Servo s3;

void setup() {
  Serial.begin(BAUDRATE);
  // SerialUSB.begin(BAUDRATE);
    
  s1.attach(servoPins::ONE);
  s2.attach(servoPins::TWO);
  s3.attach(servoPins::THREE);

  s1.write(130);
  s2.write(130);
  s3.write(130);

}

void loop() {
  SerialFlush();

  // start handshake
  Serial.println('S');

  // wait for reply
  while(Serial.available() == 0){}
  ServoStanden standen = GetServoStandenFromSerial();

  // SerialUSB.println("OK");
  // SerialUSB.print("S1: ");
  // SerialUSB.println(standen.servo1);
  // SerialUSB.print("S2: ");
  // SerialUSB.println(standen.servo2);
  // SerialUSB.print("S3: ");
  // SerialUSB.println(standen.servo3);


  s1.write(standen.servo1);
  // delay(15);
  s2.write(standen.servo2);
  // delay(15);
  s3.write(standen.servo3);
  delay(20);

  // Serial.println("OK");
  // Serial.print("S1: ");
  // Serial.println(standen.servo1);
  // Serial.print("S2: ");
  // Serial.println(standen.servo2);
  // Serial.print("S3: ");
  // Serial.println(standen.servo3);

}