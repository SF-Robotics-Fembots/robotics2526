import pyscreenshot #library for screenshots
import cv2
import keyboard #for key pressed


#frame = pyscreenshot.grab() #takes ss
#frame.save('saved_frame.png')
#frame.show('saved_frame.png')

cam = cv2.VideoCapture(1)
#resolution = (640, 480)
#fps = 40

while True:
    ret, frame = cam.read()
    if ret == True:
        cv2.imshow('photosphere cam', frame)
        if cv2.waitKey(1) == ord('q'):
            pass
        print(keyboard.read_key())

    else:
        break

while True:
    print(keyboard.read_key())

cam.release()

'''
import pyautogui
import cv2
import numpy as np
import time
import pyautogui as pg
import pygetwindow
from PIL import Image
''' 
 
'''
cam = cv2.VideoCapture(0)
width = int(cam.get(3))
height = int(cam.get(4))
resolution = (640, 480)
fps = 40 

video_out = cv2.VideoWriter("C:/Users/alyss/OneDrive/Desktop/videoframes/vidup.avi", cv2.VideoWriter_fourcc('M','J','P','G'), fps, resolution)

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


def screen_shot(self):
    random = int(time.time())
    file = "C:/Users/alyss/OneDrive/Desktop/videoframes/framesup/frame_" + str(random) + ".png"
    window = pygetwindow.getWindowsWithTitle('CAMERA GUI')[0]
    left, top = window.topleft
    right, bottom = window.bottomright
    pg.screenshot(file)
    im = Image.open(file)
    im = im.crop((left, top, right, bottom))
    im.save(file)
    im.show(file)

    cam.release()

screen_shot()
'''
#screenrecord()
#splitframes()