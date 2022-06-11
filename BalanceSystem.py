import enum
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

class Axis(enum.Enum):
    x = 0
    y = 1   


# pid class
class BalanceSystem:
    # constructor
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.Xintegral = 0
        self.Xlast_error = 0
        self.Yintegral = 0
        self.Ylast_error = 0
        self.Yerror = 0
        self.last_time = 0
        self.time = 0
        self.setPoint = Coordinate(0, 0)
        self.midpoint = Coordinate(0, 0)
    
    def setSetpoint(self, x, y):
        self.setPoint.setCoordinate(x, y)

    def setSetpoint(self, location: Coordinate):
        self.setPoint = location

    def setMidpoint(self, x, y):
        self.midpoint.setCoordinate(x, y)
    
    def setMidpoint(self, location: Coordinate):
        self.midpoint = location

    def PID(self, ballLocation: Coordinate, dt):
        def calculateAction(self, error, axis: Axis, dt):
            if axis == Axis.x:
                error_div = (error - self.Xlast_error)/dt
                self.Xintegral += (error*dt)
                self.Xlast_error = error
                return self.Kp * error + self.Ki * self.Xintegral + self.Kd * error_div
            elif axis == Axis.y:
                error_div = (error - self.Ylast_error)/dt
                self.Yintegral += (error*dt)
                self.Ylast_error = error
                return self.Kp * error + self.Ki * self.Yintegral + self.Kd * error_div
            else:
                return 0
        error = self.setPoint - ballLocation
        angle_percentageX = calculateAction(abs(error.getX()), Axis.x, dt)
        angle_percentageY = calculateAction(abs(error.getY()), Axis.y, dt)
        angleX = angle_percentageX * (180/100)
        angleY = angle_percentageY * (180/100)
        return (angleX, angleY)

if __name__ == "__main__":
    test = BalanceSystem(1, 1, 1)
    print(test.calculateAction(1, Axis.x, 1));

    exit(1)