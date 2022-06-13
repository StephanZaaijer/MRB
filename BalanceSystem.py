import enum
from hashlib import sha3_384
from math import sqrt, pow
from tkinter.tix import MAX
MAX_SERVO_CORRECTION = 10
SERVO_MID_ANGLE = 130


class Coordinate:
    # Constructor
    def __init__(self, x, y):
        self.x = x
        self.y = y
    # Getters
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getCoordinate(self):
        return (self.x, self.y)
    # Setters
    def setX(self, x):
        self.x = x
    def setY(self, y):
        self.y = y
    def setCoordinate(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)
    # String representation
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"
    # Equality check
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    # Inequality check
    def __ne__(self, other):
        return not self.__eq__(other)
    # Hash function
    def __hash__(self):
        return hash((self.x, self.y))
    # Compare function
    def __lt__(self, other):
        return self.x < other.x and self.y < other.y
    # Compare function
    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y
    # Compare function
    def __gt__(self, other):
        return self.x > other.x and self.y > other.y
    # Compare function
    def __ge__(self, other):
        return self.x >= other.x and self.y >= other.y

class Direction(enum.Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class SERVOS(enum.Enum):
    S1 = 1,
    S2 = 2,
    S3 = 3  

class ServoError():
    S1 = 0
    S2 = 0
    S3 = 0

# pid class
class BalanceSystem:
    # constructor
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.integralS1 = 0
        self.integralS2 = 0
        self.integralS3 = 0

        self.last_errorS1 = 0
        self.last_errorS2 = 0
        self.last_errorS3 = 0

        self.setPoint = Coordinate(0, 0)
        self.midpoint = Coordinate(0, 0)

        self.servoCoords: Coordinate = []

        
        self.coordinateS1: Coordinate = Coordinate(0, 0)
        self.coordinateS2: Coordinate = Coordinate(0, 0)
        self.coordinateS3: Coordinate = Coordinate(0, 0)

        self.richtingS1: Coordinate = Coordinate(0, 0)
        self.richtingS2: Coordinate = Coordinate(0, 0)
        self.richtingS3: Coordinate = Coordinate(0, 0)

    def getServoError(self, ballLocation: Coordinate):
        temp = ServoError
        # print("ballLocation: " + str(self.coordinateS1.getX()), str(self.coordinateS1.getY()))
        # print("ballLocation: " + str(self.coordinateS2.getX()), str(self.coordinateS2.getY()))
        # print("ballLocation: " + str(self.coordinateS3.getX()), str(self.coordinateS3.getY()))
        temp.S1 = ((self.setPoint.getX() - self.coordinateS1.getX()) * self.richtingS1.getX()) + ((self.setPoint.getY() - self.coordinateS1.getY()) * self.richtingS1.getY())- ((ballLocation.getX() - self.coordinateS1.getX()) * self.richtingS1.getX()) + ((ballLocation.getY() - self.coordinateS1.getY()) * self.richtingS1.getY()) 
        temp.S2 =  ((self.setPoint.getX() - self.coordinateS2.getX()) * self.richtingS2.getX()) + ((self.setPoint.getY() - self.coordinateS2.getY()) * self.richtingS2.getY())- ((ballLocation.getX() - self.coordinateS2.getX()) * self.richtingS2.getX()) + ((ballLocation.getY() - self.coordinateS2.getY()) * self.richtingS2.getY()) 
        temp.S3 = ((self.setPoint.getX() - self.coordinateS3.getX()) * self.richtingS3.getX()) + ((self.setPoint.getY() - self.coordinateS3.getY()) * self.richtingS3.getY())- ((ballLocation.getX() - self.coordinateS3.getX()) * self.richtingS3.getX()) + ((ballLocation.getY() - self.coordinateS3.getY()) * self.richtingS3.getY()) 

        # print(temp.S1, temp.S2, temp.S3)
        return temp

    def clearVariables(self):
        self.integralS1 = 0
        self.integralS2 = 0
        self.integralS3 = 0

        self.last_errorS1 = 0
        self.last_errorS2 = 0
        self.last_errorS3 = 0
    
    def setServoCoordinate(self, servo_loc: Coordinate):
        l = len(self.servoCoords)
        if l < 2:
            self.servoCoords.append(servo_loc)
        elif l == 2:
            self.servoCoords.append(servo_loc)
            self.setServoData(self.servoCoords)

    def setServoData(self, lst_servo_coordinates):
        self.coordinateS1: Coordinate = lst_servo_coordinates[0]
        self.coordinateS2: Coordinate = lst_servo_coordinates[1]
        self.coordinateS3: Coordinate = lst_servo_coordinates[2]
        
        tmpx = (self.midpoint.getX()- self.coordinateS1.getX() ) / sqrt(pow(self.coordinateS1.getX() - self.midpoint.getX(), 2) + pow(self.coordinateS1.getY() - self.midpoint.getY(), 2))
        tmpy = (self.midpoint.getY()- self.coordinateS1.getY() ) / sqrt(pow(self.coordinateS1.getX() - self.midpoint.getX(), 2) + pow(self.coordinateS1.getY() - self.midpoint.getY(), 2))

        tmpx2 = (self.midpoint.getX()- self.coordinateS2.getX() ) / sqrt(pow(self.coordinateS2.getX() - self.midpoint.getX(), 2) + pow(self.coordinateS2.getY() - self.midpoint.getY(), 2))
        tmpy2 = (self.midpoint.getY()-self.coordinateS2.getY() ) / sqrt(pow(self.coordinateS2.getX() - self.midpoint.getX(), 2) + pow(self.coordinateS2.getY() - self.midpoint.getY(), 2))

        tmpx3 = (self.midpoint.getX()- self.coordinateS3.getX()) / sqrt(pow(self.coordinateS3.getX() - self.midpoint.getX(), 2) + pow(self.coordinateS3.getY() - self.midpoint.getY(), 2))
        tmpy3 = ( self.midpoint.getY()- self.coordinateS3.getY()) / sqrt(pow(self.coordinateS3.getX() - self.midpoint.getX(), 2) + pow(self.coordinateS3.getY() - self.midpoint.getY(), 2))

        self.richtingS1: Coordinate = Coordinate(tmpx, tmpy)
        self.richtingS2: Coordinate = Coordinate(tmpx2, tmpy2)
        self.richtingS3: Coordinate = Coordinate(tmpx3, tmpy3)


    def setP(self, p):
        self.Kp = p

    def setI(self, i):
        self.Ki = i
    
    def setD(self, d):
        self.Kd = d

    def setSetpoint(self, x, y):
        self.setPoint.setCoordinate(x, y)
        # self.clearVariables()

    def setSetpoint(self, location: Coordinate):
        self.setPoint = location
        # self.clearVariables()

    def setMidpoint(self, x, y):
        self.midpoint.setCoordinate(x, y)
    
    def setMidpoint(self, location: Coordinate):
        self.midpoint = location

    def calculateActions(self, errors: ServoError, dt):
        tmp = ServoError

        error_div = (errors.S1 - self.last_errorS1)/dt

        
        self.integralS1 += (errors.S1*dt)
        if self.integralS1 > 5:
            self.integralS1 = 5
        elif self.integralS1 < -5:
            self.integralS1 = -5

        self.last_errorS1 = errors.S1
        tmp.S1 = self.Kp * errors.S1 + self.Ki * self.integralS1 + self.Kd * error_div
        
        error_div = (errors.S2 - self.last_errorS2)/dt

        
        self.integralS2 += (errors.S2*dt)
        if self.integralS2 > 5:
            self.integralS2 = 5
        elif self.integralS2 < -5:
            self.integralS2 = -5

        self.last_errorS2 = errors.S2
        tmp.S2 = self.Kp * errors.S2 + self.Ki * self.integralS2 + self.Kd * error_div

        error_div = (errors.S3 - self.last_errorS3)/dt

        self.integralS3 += (errors.S3*dt)
        if self.integralS3 > 5:
            self.integralS3 = 5
        elif self.integralS3 < -5:
            self.integralS3 = -5

        self.last_errorS3 = errors.S3
        tmp.S3 = self.Kp * errors.S3 + self.Ki * self.integralS3 + self.Kd * error_div

        print("integral", self.integralS1, self.integralS2, self.integralS3)
        # print("integrals", self.integralS1, self.integralS2, self.integralS3)
        return tmp

    def PID(self, ballLocation: Coordinate, dt):
        
        error = self.getServoError(ballLocation)
        actions: ServoError = self.calculateActions(error, dt)
        # print("actions", actions.S1, actions.S2, actions.S3)
        print(actions.S1)
        angleS1 = SERVO_MID_ANGLE - (actions.S1 * (MAX_SERVO_CORRECTION/100) )
        angleS2 = SERVO_MID_ANGLE - (actions.S2 * (MAX_SERVO_CORRECTION/100) )
        angleS3 = SERVO_MID_ANGLE - (actions.S3 * (MAX_SERVO_CORRECTION/100) )

        # print("angles", angleS1, angleS2, angleS3)

        if angleS1 > (SERVO_MID_ANGLE + MAX_SERVO_CORRECTION):
            angleS1 = SERVO_MID_ANGLE + MAX_SERVO_CORRECTION

        elif angleS1 < (SERVO_MID_ANGLE - MAX_SERVO_CORRECTION):
            angleS1 = SERVO_MID_ANGLE - MAX_SERVO_CORRECTION
        ####
        if angleS2 > (SERVO_MID_ANGLE + MAX_SERVO_CORRECTION):
            angleS2 = SERVO_MID_ANGLE + MAX_SERVO_CORRECTION

        elif angleS2 < (SERVO_MID_ANGLE - MAX_SERVO_CORRECTION):
            angleS2 = SERVO_MID_ANGLE - MAX_SERVO_CORRECTION
        ####
        if angleS3 > (SERVO_MID_ANGLE + MAX_SERVO_CORRECTION):
            angleS3 = SERVO_MID_ANGLE + MAX_SERVO_CORRECTION

        elif angleS3 < (SERVO_MID_ANGLE - MAX_SERVO_CORRECTION):
            angleS3 = SERVO_MID_ANGLE - MAX_SERVO_CORRECTION 

        # print("modified angles", angleS1, angleS2, angleS3)
        
        return [int(angleS1), int(angleS2), int(angleS3)]
    
if __name__ == "__main__":
    exit(1)