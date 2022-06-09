#include "BalanceSystem.hpp"

BalanceSystem::BalanceSystem(const Servo& s1, const Servo& s2, const Servo& s3, const float &kp, const float &ki, const float &kd):
    s1(s1), 
    s2(s2), 
    s3(s3),
    kp(kp),
    ki(ki),
    kd(kd)
{}

int BalanceSystem::calculateAction(int error, axis axis, unsigned long dt){
    int result = 0;
    switch(axis){
        case X:
            errorSumX += error*dt;
            errorDivX = (error - errorPrevX)/dt;
            result = kp * error + ki * errorSumX + kd * errorDivX;
            break;
        case Y:
            errorSumY += error*dt;
            errorDivY = (error - errorPrevY)/dt;
            result = kp * error + ki * errorSumY + kd * errorDivY;
            break;
    }
    return result;
}

void BalanceSystem::PID(Location ballLocation, unsigned long dt){
    Location error = setPoint - ballLocation;
    int angle_percentageX = calculateAction(abs(error.x), X, dt);
    int angle_percentageY = calculateAction(abs(error.y), Y, dt);

    float angleX = angle_percentageX * (180/100);
    float angleY = angle_percentageY * (180/100);

    if(error.x > 0){
        tiltX(angleX, direction::LEFT);
    }
    else if(error.x < 0){
        tiltX(angleX, direction::RIGHT);
    }
    else{
        // x point reached, do nothing
    }
    
    if(error.y > 0){
        tiltY(angleY, direction::FORWARD);
    }
    else if(error.y < 0){
        tiltY(angleY, direction::BACKWARD);
    }
    else{
        // y point reached, do nothing
    }
}

void BalanceSystem::setMidpoint(const Location& midpoint){
    midPoint = midpoint;
}

void BalanceSystem::setSetpoint(const Location& setpoint){
    setPoint = setpoint;
}

void BalanceSystem::tiltX(float angle, direction dir){
    float opposite_angle = 180-angle;
    if (dir == direction::LEFT){
        s2.write(angle);

        s1.write( opposite_angle );
        s3.write( opposite_angle );
    }

    else{
        s2.write( opposite_angle );
        
        s1.write(angle);
        s3.write(angle);
    }
}

void BalanceSystem::tiltY(float angle, direction dir){
    float opposite_angle = 180-angle;

    if (dir == direction::FORWARD){
        s1.write(opposite_angle);
        s3.write(angle);
    }
    
    else{
        s1.write( angle );
        s3.write( opposite_angle );
    }
}
