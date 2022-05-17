import cv2
import json
import numpy as np

def capture(cam):
    check, frame = cam.read()
    return frame

def filter_img(frame, low_tresh, high_tresh):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
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
                }



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


####### this code is an alternative for the lines beneath, but its not very robust ######
# cv2.namedWindow('controls')

# for key, value in hsv.items():
#     cv2.createTrackbar(key, 'controls', value, hsv['high ' + key[-1]], eval(f'{key[-1]}'))

#######                                                                            ######

if __name__ == "__main__":
    cv2.namedWindow('controls')

    hsv = load_values('values.txt')
    maxH = 255
    maxS = 255
    maxV = 255

    names = ['low H', 'high H', 'low S', 'high S', 'low V', 'high V']

    cv2.createTrackbar('low H','controls',hsv['low H'], maxH,callbackH)
    cv2.createTrackbar('high H','controls',hsv['high H'], maxH,callbackH)
    cv2.createTrackbar('low S','controls',hsv['low S'], maxS,callbackS)
    cv2.createTrackbar('high S','controls',hsv['high S'], maxS,callbackS)
    cv2.createTrackbar('low V','controls',hsv['low V'], maxV,callbackV)
    cv2.createTrackbar('high V','controls',hsv['high V'], maxV,callbackV)

    cam = cv2.VideoCapture(0)
    while(True):
        img = capture(cam)

        hsv_low = np.array([hsv['low H'], hsv['low S'], hsv['low V']])
        hsv_high = np.array([hsv['high H'], hsv['high S'], hsv['high V']])

        res = filter_img(img, hsv_low, hsv_high)

        cv2.imshow('original', img)
        cv2.imshow('res', res)

        k = cv2.waitKey(1)
        if k == 27:
            break
    cv2.destroyAllWindows()
    write_values('values.txt', hsv)

