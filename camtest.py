import cv2
import json
import numpy as np
import serial

def callbackH(x):
    global hsv
    
    hsv['low H'] = cv2.getTrackbarPos('low H','controls')
    hsv['high H'] = cv2.getTrackbarPos('high H','controls')

def callbackS(x):
    global hsv
    
    hsv['low S'] = cv2.getTrackbarPos('low S','controls')
    hsv['high S'] = cv2.getTrackbarPos('high S','controls')

def callbackV(x):
    global hsv

    hsv['low V'] = cv2.getTrackbarPos('low V','controls')
    hsv['high V'] = cv2.getTrackbarPos('high V','controls')

def callbackRad(x):
    global hsv
    hsv['min Rad'] = cv2.getTrackbarPos('min Rad','controls')
    hsv['max Rad'] = cv2.getTrackbarPos('max Rad','controls')

def callbackDist(x):
    global hsv
    temp = cv2.getTrackbarPos('min Dist','controls')
    if (temp==0):
        hsv['min Dist'] = 1
    else:
        hsv['min Dist'] = temp


def capture(cam):
    check, frame = cam.read()
    return frame

def detect_circles(img, minRadius, maxRadius, minDist):
    output = img.copy()
    x_gem = None
    y_gem = None
    # image = cv2.cvtColor(output, cv2.COLOR_HSV2RGB)
    image = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(image=image, 
                           method=cv2.HOUGH_GRADIENT, 
                           dp=1.5, 
                           minDist=minDist,
                           param1=50,
                           param2=50,
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

def load_values(filename):
    try:
        with open(f'{filename}', 'r') as infile:
            return json.load(infile)
    except FileNotFoundError:
        print(f"['{filename}'] does not exit. using default values...\nHint: never written to '{filename}'?")
        return {
                "low H" : 0,
                "high H" : 255,
                "low S" : 0,
                "high S" : 255,
                "low V" : 0,
                "high V" : 255,
                "min Rad": 1,
                "max Rad": 1000,
                "min Dist": 1
                }


####### this code is an alternative for the lines beneath, but its not very robust ######
# cv2.namedWindow('controls')

# for key, value in hsv.items():
#     cv2.createTrackbar(key, 'controls', value, hsv['high ' + key[-1]], eval(f'{key[-1]}'))

#######                                                                            ######
if __name__ == "__main__":
    
    conn = serial.Serial('COM14', 19200, timeout=1)
    conn.flush()
    
    cv2.namedWindow('controls')

    hsv = load_values('values.json')
    maxH = 255
    maxS = 255
    maxV = 255
    maxRad = 1000
    maxDist = 1000

    names = ['low H', 'high H', 'low S', 'high S', 'low V', 'high V', 'min Rad', 'max Rad', 'min Dist']

    cv2.createTrackbar('low H','controls',hsv['low H'], maxH,callbackH)
    cv2.createTrackbar('high H','controls',hsv['high H'], maxH,callbackH)
    
    cv2.createTrackbar('low S','controls',hsv['low S'], maxS,callbackS)
    cv2.createTrackbar('high S','controls',hsv['high S'], maxS,callbackS)
    
    cv2.createTrackbar('low V','controls',hsv['low V'], maxV,callbackV)
    cv2.createTrackbar('high V','controls',hsv['high V'], maxV,callbackV)
    
    cv2.createTrackbar('min Rad','controls',hsv['min Rad'], maxRad,callbackRad)
    cv2.createTrackbar('max Rad','controls',hsv['max Rad'], maxRad,callbackRad)
    
    cv2.createTrackbar('min Dist','controls',hsv['min Dist'], maxDist,callbackDist)
    
    

    cam = cv2.VideoCapture(1)
    if cam is None or not cam.isOpened():
        print("failed to open camera")
        return
      
    while(True):
        img = capture(cam)

        hsv_low = np.array([hsv['low H'], hsv['low S'], hsv['low V']])
        hsv_high = np.array([hsv['high H'], hsv['high S'], hsv['high V']])

        res = filter_img(img, hsv_low, hsv_high)
                
        res, gem_loc = detect_circles(res, hsv['min Rad'], hsv['max Rad'], hsv['min Dist'])

        if gem_loc != (None, None):
            conn.write(gem_loc)
        cv2.imshow('original', img)
        cv2.imshow('res', res)

        k = cv2.waitKey(1)
        if k == 27:
            break
    cv2.destroyAllWindows()
    write_values('values.json', hsv)
    conn.close()