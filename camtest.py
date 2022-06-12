from venv import create
import cv2
import json
import time
import serial
import enum
import numpy as np
from BalanceSystem import BalanceSystem, Coordinate

# global variables
SERVO_MID_ANGLE = 120

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



# def click_event(event, x, y, flags, params):
 
#     # checking for left mouse clicks
#     if event == cv2.EVENT_LBUTTONDOWN:


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



    return img, (x_gem , y_gem )

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

def sendDataToServos(conn, gem_loc, angle_correction):
    # wait for handshake
    while conn.read() != 'S': {}

    # get error correcitons
    x = angle_correction.getX()
    y = angle_correction.getY()

    # store x servo state because it has to remain the same when changing y
    x_servo_state = int()

    # write x error correction to serial
    if x >= 0:
        x_servo_state = 120 + x
        conn.write(f"{120-x} {120+x} {120-x}")
    elif x < 0:
        x_servo_state = 120 - x
        conn.write(f"{120+x} {120-x} {120+x}")
    
    # wait for handshake
    while conn.read() != 'S': {}

    # write y error correction to serial
    # keep x servo state the same
    if y >= 0:
        conn.write(f"{120-y} {x_servo_state} {120+y}")
    elif y < 0:
        conn.write(f"{120+y} {x_servo_state} {120-y}")

    return True

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

####### this code is an alternative for the lines beneath, but its not very robust ######
# cv2.namedWindow('controls')

# for key, value in hsv.items():
#     cv2.createTrackbar(key, 'controls', value, hsv['high ' + key[-1]], eval(f'{key[-1]}'))

#######                                                                            ######
if __name__ == "__main__":
    system = BalanceSystem(0.1, 0.1, 0.1)
    
    # cv2.setMouseCallback('image', click_event)
    
    # conn = serial.Serial('COM14', 19200, timeout=1)
    # conn.flush()
    hsv = load_values('values.json')
    
    dt = float('-inf')
    cam = cv2.VideoCapture(1)
    if cam is None or not cam.isOpened():
        print("failed to open camera")
        quit()

    # determine midpoint of plane
    cv2.namedWindow('controls', cv2.WINDOW_NORMAL)
    create_controls(hsv, HSV(FILTER.MIDPOINT))
    while(True):
        t = time.perf_counter()
        img = capture(cam)

        hsv_mid = hsv['midpoint_filter']

        hsv_low = np.array([hsv_mid['low H'], hsv_mid['low S'], hsv_mid['low V']])
        hsv_high = np.array([hsv_mid['high H'], hsv_mid['high S'], hsv_mid['high V']])

        res = filter_img(img, hsv_low, hsv_high)
                
        res, gem_loc = detect_circles(res, hsv_mid['min Rad'], hsv_mid['max Rad'], hsv_mid['min Dist'], hsv_mid['dp'], hsv_mid['param1'], hsv_mid['param2'])

        cv2.imshow('original', img)
        cv2.imshow('MIDPOINT FILTER', res)

        k = cv2.waitKey(1)
        if k == 27:
            cv2.destroyAllWindows()
            write_values('values.json', hsv)

            samplesX = []
            samplesY = []
            for i in range(60):
                res = filter_img(img, hsv_low, hsv_high)
                res, gem_loc = detect_circles(res, hsv_mid['min Rad'], hsv_mid['max Rad'], hsv_mid['min Dist'], hsv_mid['dp'], hsv_mid['param1'], hsv_mid['param2'])
                samplesX.append(gem_loc[0])
                samplesY.append(gem_loc[1])

            x = np.median(samplesX)
            y = np.median(samplesY)
            print(f"coordinate: ({x}, {y})")
            system.setMidpoint(Coordinate(x, y))
            break
            


    # track ball location
    cv2.namedWindow('controls', cv2.WINDOW_NORMAL)
    create_controls(hsv, HSV(FILTER.BALL))
    while(True):
        t = time.perf_counter()
        img = capture(cam)

        hsv_ball = hsv['ball_filter']

        hsv_low = np.array([hsv_ball['low H'], hsv_ball['low S'], hsv_ball['low V']])
        hsv_high = np.array([hsv_ball['high H'], hsv_ball['high S'], hsv_ball['high V']])

        res = filter_img(img, hsv_low, hsv_high)
                
        res, gem_loc = detect_circles(res, hsv_ball['min Rad'], hsv_ball['max Rad'], hsv_ball['min Dist'], hsv_ball['dp'], hsv_ball['param1'], hsv_ball['param2'])

        # if gem_loc != (None, None):
        #     print(gem_loc)
        #     new_t = time.perf_counter()
        #     dt = new_t - t
        #     check, angle_correction = system.PID(Coordinate(gem_loc[0], gem_loc[1]), dt)

        #     # write corrections to serial
        #     if check:
        #         print(gem_loc)
        #         sendDataToServos(conn, gem_loc, angle_correction)

        cv2.imshow('original', img)
        cv2.imshow('BALL FILTER', res)

        k = cv2.waitKey(1)
        if k == 27:
            break
    cv2.destroyAllWindows()
    write_values('values.json', hsv)
    # conn.close()