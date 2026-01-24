import pyautogui
import cv2
import numpy as np
import time

cam = cv2.VideoCapture(1)
width = int(cam.get(3))
height = int(cam.get(4))
resolution = (640, 480)
fps = 40

video_out = cv2.VideoWriter("C:/Users/alyss/OneDrive/Desktop/videoframes/viddown.avi", cv2.VideoWriter_fourcc('M','J','P','G'), fps, resolution)

def screenrecord():
    while True:
        ret, frame = cam.read()
        if ret == True:
            video_out.write(frame)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) == ord('q'):
                break
        else:
            break

    cam.release()
    video_out.release()
    #cv2.destroyAllWindows('frame')

def splitframes():
    capture = cv2.VideoCapture('C:/Users/alyss/OneDrive/Desktop/videoframes/viddown.avi')
    frameNr = 0
    success, frame = capture.read()
    success = True
    while success:
        capture.set(cv2.CAP_PROP_POS_MSEC, (frameNr * 1000))
        success, frame = capture.read()
        cv2.imwrite(f'C:/Users/alyss/OneDrive/Desktop/videoframes/framesdown/frame_{frameNr}.png', frame)
 
        frameNr = frameNr+1
        #time.sleep(5)

 
    capture.release()

screenrecord()
splitframes()