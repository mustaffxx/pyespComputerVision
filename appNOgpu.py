from collections import deque
from imutils.video import VideoStream
import numpy as np
import cv2
import argparse
import imutils
import time
import serial

def nothing(x):
    pass

#serial port for communication with ESP32
ser = serial.Serial('COM4', 115200, timeout = 1)

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type = int, default = 64,
                help = "max buffer size")
args = vars(ap.parse_args())
pts = deque(maxlen = args["buffer"])

if not args.get("video", False):
    vs = VideoStream(src = 0).start()
else:
    vs = cv2.VideoCapture(args["video"])

time.sleep(2.0)

#create a window for the trackbars of color
cv2.namedWindow('frame')
cv2.createTrackbar('R','frame', 0, 255, nothing)
cv2.createTrackbar('G','frame', 0, 255, nothing)
cv2.createTrackbar('B','frame', 0, 255, nothing)
cv2.createTrackbar('R1','frame', 0, 255, nothing)
cv2.createTrackbar('G1','frame', 0, 255, nothing)
cv2.createTrackbar('B1','frame', 0, 255, nothing)

while(True):
    # Capture frame-by-frame
    frame = vs.read()

    frame = frame[1] if args.get("video", False) else frame

    if frame is None:
        break

    frame = imutils.resize(frame, width = 600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    #lower range
    r = cv2.getTrackbarPos('R', 'frame')
    g = cv2.getTrackbarPos('G', 'frame')
    b = cv2.getTrackbarPos('B', 'frame')

    #upper range
    r1 = cv2.getTrackbarPos('R1', 'frame')
    g1 = cv2.getTrackbarPos('G1', 'frame')
    b1 = cv2.getTrackbarPos('B1', 'frame')
    
    lowervalue = np.array([r, g, b])
    uppervalue = np.array([r1, g1, b1])

    '''
    lines created to display boundaries in the window
    cv2.line(frame, (260, 0), (260, 450), (255, 0, 0), 3)
    cv2.line(frame, (340, 0), (340, 450), (255, 0, 0), 3)
    cv2.line(frame, (0, 185), (600, 185), (255, 0, 0), 3)
    cv2.line(frame, (0, 265), (600, 265), (255, 0, 0), 3)
    '''
    
    mask = cv2.inRange(hsv, lowervalue, uppervalue)
    mask = cv2.erode(mask, None, iterations = 2)
    mask = cv2.dilate(mask, None, iterations = 2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    center = None

    if len(cnts) > 0:
        c = max(cnts, key = cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
            #r1 and r2 are the radii of the circles
            r1 = 40
            r2 = 5
            cv2.circle(frame, (300, 225), r1, (0, 0, 255), 3)

            #this part calculate the distance between the color and the circle in center
            d = np.sqrt(((center[0] - 300)**2) + ((center[1] - 225)**2))

            #check whether it is in, out, or overlapping
            if d > (r1 + r2):
                #print("Blue circle does not overlap Red circle")
                pass

            elif (d <= np.abs(r1 - r2)):
                #print("Blue circle is inside Red circle")
                cv2.circle(frame, (300, 225), r1, (255, 0, 0), 3)
            else:
                #print("Blue circle overlaps Red circle")
                cv2.circle(frame, (300, 225), r1, (0, 255, 0), 3)

            text = 'NOT'
            comm = 7
            
            #statements what define the boundaries and send commands to ESP32
            if center[0] < 260 and center[1] < 185:
                text = 'left top'
                comm = 5
            elif center[0] < 260 and center[1] > 265:
                text = 'left bottom'
                comm = 6
            elif center[0] > 340 and center[1] < 185:
                text = 'top right'
                comm = 7
            elif center[0] > 340 and center[1] > 265:
                text = 'top bottom'
                comm = 8
            elif center[0] < 260:
                text = 'left'
                comm = 1
            elif center[0] > 340:
                text = 'right'
                comm = 2
            elif center[1] < 185:
                text = 'top'
                comm = 3
            elif center[1] > 265:
                text = 'bottom'
                comm = 4
            else:
                text = 'center'
                comm = 0

            ser.write(b'%i'%comm)
            ser.flush()
            #print(ser.readline().decode("UTF-8"))
            cv2.putText(frame, text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
                        2, cv2.LINE_AA)
                
            
   
    pts.appendleft(center)

    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue

        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        ser.close()
        break

if not args.get("video", False):
    vs.stop()

else:
    vs.release()

cv2.destroyAllWindows()
