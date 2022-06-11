#ifndef DEFINITIONS_HPP
#define DEFINITIONS_HPP

#define BAUDRATE 19200
#define SAMPLES_PER_SECOND 60

#define Ki 0.1
#define Kp 0.1
#define Kd 0.1

enum direction {
  FORWARD,
  BACKWARD,
  LEFT,
  RIGHT
};

enum axis {
    X,
    Y
};

enum servoPins {
    ONE = 5,
    TWO = 6,
    THREE = 9,
};
#endif //DEFINITIONS_HPP