#ifndef BALANCESYSTEM_HPP
#define BALANCESYSTEM_HPP

#include <Servo.h>
#include <Arduino.h>
#include "Location.hpp"
#include "Definitions.hpp"


/**
 * @brief      Class for balance system.
 * @details    This class is used to balance the robot. The layout of the motors are as follows:
 * @image html MRB_motor_layout.png
 * @details    The balance system contains a PID controller. This PID controller is used to control the motors.
 * @details    The motors are precicely alligned so that S2 is exaclty on the X-axis. This way, motor S2 does not have to move when S1 and S3 are moving the system forwards and backwards.
 */
class BalanceSystem{
    
    public:
        BalanceSystem(const Servo& s1, const Servo& s2, const Servo& s3, const float &kp, const float &ki, const float &kd);
        void PID(Location ballLocation, unsigned long dt);
        int calculateAction(int error, axis axis, unsigned long dt);
        void setMidpoint(const Location& midpoint);
        void setSetpoint(const Location& setpoint);

    private:
        Servo s1;
        Servo s2;
        Servo s3;

        Location midPoint;
        Location setPoint;

        void tiltX(float angle, direction dir);
        void tiltY(float angle, direction dir);
        
        int kp;
        int ki;
        int kd;

        int errorX = 0;
        int errorY = 0;
        
        int errorSumX = 0;
        int errorDivX = 0;
        int errorPrevX = 0;

        int errorSumY = 0;
        int errorDivY = 0;
        int errorPrevY = 0;


};


#endif //BALANCESYSTEM_HPP