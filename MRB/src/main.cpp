#include <Arduino.h>
#include <Servo.h>
#include "Definitions.hpp"
// #include "Location.hpp"
// #include "BalanceSystem.hpp"

// #define DEBUG

struct ServoStanden{
  int servo1;
  int servo2;
  int servo3;
};


void SerialFlush(){
  while(SerialUSB.available()){
    SerialUSB.read();
  }
}

ServoStanden GetServoStandenFromSerial(){
  ServoStanden standen;
  standen.servo1 = SerialUSB.parseInt();
  // standen.servo2 = SerialUSB.parseInt();
  // standen.servo3 = SerialUSB.parseInt();
  return standen;
}

Servo s1;
Servo s2;
Servo s3;
// BalanceSystem sys(s1, s2, s3, Ki, Kp, Kd);

void setup() {
  SerialUSB.begin(BAUDRATE);
  pinMode(servoPins::ONE, OUTPUT);
  pinMode(servoPins::TWO, OUTPUT);
  pinMode(servoPins::THREE, OUTPUT);
  
  s1.attach(servoPins::ONE);
  s2.attach(servoPins::TWO);
  s3.attach(servoPins::THREE);
}

void loop() {
  SerialFlush();
  while(SerialUSB.available() == 0){}
  ServoStanden standen = GetServoStandenFromSerial();

  s1.write(standen.servo1);
  s2.write(standen.servo2);
  s3.write(standen.servo3);

  SerialUSB.println("OK");
  SerialUSB.print("S1: ");
  SerialUSB.println(standen.servo1);
  SerialUSB.print("S2: ");
  SerialUSB.println(standen.servo2);
  SerialUSB.print("S3: ");
  SerialUSB.println(standen.servo3);

}