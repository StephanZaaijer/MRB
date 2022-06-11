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
    
  s1.attach(servoPins::ONE);
  s2.attach(servoPins::TWO);
  s3.attach(servoPins::THREE);

}

int angle = 80;
void loop() {
  
  SerialFlush();
  while(Serial.available() == 0){}
  ServoStanden standen = GetServoStandenFromSerial();

  s1.write(standen.servo1);
  delay(15);
  s2.write(standen.servo2);
  delay(15);
  s3.write(standen.servo3);
  delay(20);

  Serial.println("OK");
  Serial.print("S1: ");
  Serial.println(standen.servo1);
  Serial.print("S2: ");
  Serial.println(standen.servo2);
  Serial.print("S3: ");
  Serial.println(standen.servo3);

}