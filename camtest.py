from re import A
from venv import create
import cv2
import json
import time
import serial
import enum
import numpy as np
from BalanceSystem import BalanceSystem, Coordinate

# global variables
SERVO_MID_ANGLE = 130
CLICK_SETTING = ""


maxH = 255
maxS = 255
maxV = 255
maxRad = 1000
maxDist = 1000
maxdp = 100
maxparam1 = 200
maxparam2 = 200

##################
class FILTER(enum.Enum):
    MIDPOINT = 0,
    BALL = 1

class HSV():
    def __init__(self, filter):
        self.filter : FILTER = filter
    
    def get_filter(self):
        if self.filter == FILTER.MIDPOINT:
            return "midpoint_filter"
        else:
            return "ball_filter"


def callbackH(hsv_setting : HSV):
    global hsv
    hsv[hsv_setting.get_filter()]['low H'] = cv2.getTrackbarPos('low H','controls')
    hsv[hsv_setting.get_filter()]['high H'] = cv2.getTrackbarPos('high H','controls')

def callbackS(hsv_setting : HSV):
    global hsv
    hsv[hsv_setting.get_filter()]['low S'] = cv2.getTrackbarPos('low S','controls')
    hsv[hsv_setting.get_filter()]['high S'] = cv2.getTrackbarPos('high S','controls')

def callbackV(hsv_setting : HSV):
    global hsv
    hsv[hsv_setting.get_filter()]['low V'] = cv2.getTrackbarPos('low V','controls')
    hsv[hsv_setting.get_filter()]['high V'] = cv2.getTrackbarPos('high V','controls')

def callbackRad(hsv_setting : HSV):
    global hsv
    hsv[hsv_setting.get_filter()]['min Rad'] = cv2.getTrackbarPos('min Rad','controls')
    hsv[hsv_setting.get_filter()]['max Rad'] = cv2.getTrackbarPos('max Rad','controls')

def callbackDist(hsv_setting : HSV):
    global hsv
    temp = cv2.getTrackbarPos('min Dist','controls')
    if (temp==0):
        hsv[hsv_setting.get_filter()]['min Dist'] = 1
    else:
        hsv[hsv_setting.get_filter()]['min Dist'] = temp

def callbackdp(hsv_setting : HSV):
    global hsv
    tmp = cv2.getTrackbarPos('dp_factor10','controls')
    if (tmp==0):
        hsv[hsv_setting.get_filter()]['dp'] = 1
    else:
        hsv[hsv_setting.get_filter()]['dp'] = tmp

def callbackparam1(hsv_setting : HSV):
    global hsv
    tmp = cv2.getTrackbarPos('param1','controls')
    if (tmp==0):
        hsv[hsv_setting.get_filter()]['param1'] = 1
    else:
        hsv[hsv_setting.get_filter()]['param1'] = tmp

def callbackparam2(hsv_setting : HSV):
    global hsv
    tmp = cv2.getTrackbarPos('param2','controls')
    if (tmp==0):
        hsv[hsv_setting.get_filter()]['param2'] = 1
    else:
        hsv[hsv_setting.get_filter()]['param2'] = tmp

def callbackP(x):
    global system
    system.setP(x)

def callbackI(x):
    global system
    system.setI(x)

def callbackD(x):
    global system
    system.setD(x)



def click_event(event, x, y, flags, params):
    global system
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"{x}, {y}")
        if CLICK_SETTING == "servo":
            system.setServoCoordinate(Coordinate(x, y))
        elif CLICK_SETTING == "setpoint":
            system.setSetpoint(Coordinate(x, y))



def capture(cam):
    check, frame = cam.read()
    return frame

def detect_circles(img, minRadius, maxRadius, minDist, dp, param1, param2):
    output = img.copy()
    x_gem = None
    y_gem = None
    # image = cv2.cvtColor(output, cv2.COLOR_HSV2RGB)
    output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(image=output, 
                           method=cv2.HOUGH_GRADIENT, 
                           dp=(dp/10), 
                           minDist=minDist,
                           param1=param1,
                           param2=param2,
                           minRadius=minRadius,
                           maxRadius=maxRadius                           
                          )
    x_gem = None
    y_gem = None
    if circles is not None:
        sum_x=0
        sum_y=0
        circles_round =  np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles_round:
            # draw the outer circle
            cv2.circle(img, (x, y), r, (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(img,(x, y),2,(0,0,255),3)
            sum_x+=x
            sum_y+=y
        
        
        x_gem = int(sum_x/len(circles_round))
        y_gem  = int(sum_y/len(circles_round))
        
        cv2.circle(img,(x_gem , y_gem),2,(255,255,255),3)

    return img, (x_gem , y_gem ), 

def filter_img(frame, low_tresh, high_tresh):
    # median filter to remove salt&pepper
    median = cv2.medianBlur(frame, 5)

    # color conversion and selection\
    hsv = cv2.cvtColor(median, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low_tresh, high_tresh)
    result = cv2.bitwise_and(frame, frame, mask = mask)

    return result

def write_values(filename, values):
    with open(f'{filename}', 'w') as outfile:
        js = json.dumps(values, indent=4)
        outfile.write(js)

def load_values(filename):
    try:
        with open(f'{filename}', 'r') as infile:
            return json.load(infile)
    except FileNotFoundError:
        print(f"['{filename}'] does not exit. using default values...\nHint: never written to '{filename}'?")
        return {
                "ball_filter": {"low H": 0,"high H": 255,"low S": 0,"high S": 255,"low V": 0,"high V": 255,"min Rad": 1,"max Rad": 200,"min Dist": 1,"dp": 15,"param1": 100,"param2": 200},
                "midpoint_filter": {"low H": 0,"high H": 255,"low S": 0,"high S": 255,"low V": 0,"high V": 255,"min Rad": 1,"max Rad": 200,"min Dist": 1,"dp": 15,"param1": 100,"param2": 200}
            }


def create_controls(hsv, hsv_setting : HSV):
    cv2.createTrackbar('low H','controls',hsv[hsv_setting.get_filter()]['low H'], maxH,lambda x: callbackH(hsv_setting))
    cv2.createTrackbar('high H','controls',hsv[hsv_setting.get_filter()]['high H'], maxH,lambda x: callbackH(hsv_setting))
    
    cv2.createTrackbar('low S','controls',hsv[hsv_setting.get_filter()]['low S'], maxS, lambda x: callbackS(hsv_setting))
    cv2.createTrackbar('high S','controls',hsv[hsv_setting.get_filter()]['high S'], maxS, lambda x: callbackS(hsv_setting))
    
    cv2.createTrackbar('low V','controls',hsv[hsv_setting.get_filter()]['low V'], maxV, lambda x: callbackV(hsv_setting))
    cv2.createTrackbar('high V','controls',hsv[hsv_setting.get_filter()]['high V'], maxV, lambda x: callbackV(hsv_setting))
    
    cv2.createTrackbar('min Rad','controls',hsv[hsv_setting.get_filter()]['min Rad'], maxRad, lambda x: callbackRad(hsv_setting))
    cv2.createTrackbar('max Rad','controls',hsv[hsv_setting.get_filter()]['max Rad'], maxRad, lambda x: callbackRad(hsv_setting))
    
    cv2.createTrackbar('min Dist','controls',hsv[hsv_setting.get_filter()]['min Dist'], maxDist, lambda x: callbackDist(hsv_setting))

    cv2.createTrackbar('dp_factor10','controls',hsv[hsv_setting.get_filter()]['dp'], maxdp, lambda x: callbackdp(hsv_setting))
    
    cv2.createTrackbar('param1','controls',hsv[hsv_setting.get_filter()]['param1'], maxparam1, lambda x: callbackparam1(hsv_setting))
    cv2.createTrackbar('param2','controls',hsv[hsv_setting.get_filter()]['param2'], maxparam2, lambda x: callbackparam2(hsv_setting))

    cv2.createTrackbar('p','controls',0, 30, callbackP)
    cv2.createTrackbar('i','controls',0, 30, callbackI)
    cv2.createTrackbar('d','controls',0, 30, callbackD)
    


if __name__ == "__main__":
    mid = Coordinate(300, 300)
    system = BalanceSystem(0.5, 0, 0)  # default setpoint is equal to midpoint

    s1, s2, s3 = Coordinate(1, 0), Coordinate(1, 600), Coordinate(900, 300) 
    system.setServoCoordinate(s1)
    system.setServoCoordinate(s2)
    system.setServoCoordinate(s3)
    system.setMidpoint(mid)

    angle_correction = system.PID(Coordinate(1, 600), 0.03)
    print(angle_correction)

    # conn = serial.Serial('COM14', 115200, timeout=1)

    # hsv = load_values('values.json')
    
    # dt = float('-inf')
    # cam = cv2.VideoCapture(1)
    # if cam is None or not cam.isOpened():
    #     print("failed to open camera")
    #     quit()

    # # determine midpoint of plane
    # cv2.namedWindow('controls', cv2.WINDOW_NORMAL)
    # cv2.namedWindow('MIDPOINT FILTER')

    # cv2.setMouseCallback('MIDPOINT FILTER', click_event)
    # create_controls(hsv, HSV(FILTER.MIDPOINT))
    # while(True):
    #     CLICK_SETTING = "servo"

    #     t = time.perf_counter()
    #     img = capture(cam)

    #     hsv_mid = hsv['midpoint_filter']

    #     hsv_low = np.array([hsv_mid['low H'], hsv_mid['low S'], hsv_mid['low V']])
    #     hsv_high = np.array([hsv_mid['high H'], hsv_mid['high S'], hsv_mid['high V']])

    #     res = filter_img(img, hsv_low, hsv_high)
                
    #     res, gem_loc = detect_circles(res, hsv_mid['min Rad'], hsv_mid['max Rad'], hsv_mid['min Dist'], hsv_mid['dp'], hsv_mid['param1'], hsv_mid['param2'])

    #     cv2.imshow('original', img)
    #     cv2.imshow('MIDPOINT FILTER', res)

    #     k = cv2.waitKey(1)
    #     if k == 27:
    #         cv2.destroyAllWindows()
    #         write_values('values.json', hsv)

    #         samplesX = []
    #         samplesY = []
    #         for i in range(60):
    #             res = filter_img(img, hsv_low, hsv_high)
    #             res, gem_loc = detect_circles(res, hsv_mid['min Rad'], hsv_mid['max Rad'], hsv_mid['min Dist'], hsv_mid['dp'], hsv_mid['param1'], hsv_mid['param2'])
    #             samplesX.append(gem_loc[0])
    #             samplesY.append(gem_loc[1])

    #         x = np.median(samplesX)
    #         y = np.median(samplesY)
    #         system.setMidpoint(Coordinate(x, y))

    #         # Set setpoint to midpoint as default
    #         print(f"setpoint: ({x}, {y})")
    #         system.setSetpoint(Coordinate(x, y))
    #
    #         break
            
    # # track ball location
    # cv2.namedWindow('controls', cv2.WINDOW_NORMAL)
    # cv2.namedWindow('BALL FILTER')
    # cv2.setMouseCallback('BALL FILTER', click_event)

    # create_controls(hsv, HSV(FILTER.BALL))
    # t = time.perf_counter()
    # # counter = 1
    # while(True):
    #     CLICK_SETTING = "ball"
    #     img = capture(cam)

    #     hsv_ball = hsv['ball_filter']

    #     hsv_low = np.array([hsv_ball['low H'], hsv_ball['low S'], hsv_ball['low V']])
    #     hsv_high = np.array([hsv_ball['high H'], hsv_ball['high S'], hsv_ball['high V']])

    #     res = filter_img(img, hsv_low, hsv_high)
                
    #     res, gem_loc = detect_circles(res, hsv_ball['min Rad'], hsv_ball['max Rad'], hsv_ball['min Dist'], hsv_ball['dp'], hsv_ball['param1'], hsv_ball['param2'])

    #     if gem_loc != (None, None):
    #         # print(gem_loc)
            
    #         # write corrections to serial
    #         while conn.read() != B'S': {}

    #         new_t = time.perf_counter()
    #         dt = new_t - t
    #         # print(dt)
    #         angle_correction = system.PID(Coordinate(gem_loc[0], gem_loc[1]), dt)
    #         print(f"angle correction: {angle_correction}")
    #         # print("sending")
    #         if angle_correction != None:
    #             conn.write(f"{angle_correction[0]} ".encode('utf-8'))
    #             conn.write(f"{angle_correction[1]} ".encode('utf-8'))
    #             conn.write(f"{angle_correction[2]} ".encode('utf-8'))
    #             conn.write('\n'.encode('utf-8'))
    #             # counter += 1
    #             t = time.perf_counter()
    #             # time.sleep(1/60)
    #     # print(counter)

    #     cv2.imshow('original', img)
    #     cv2.imshow('BALL FILTER', res)

    #     k = cv2.waitKey(1)
    #     if k == 27:
    #         break
    # cv2.destroyAllWindows()
    # write_values('values.json', hsv)
    # conn.close()