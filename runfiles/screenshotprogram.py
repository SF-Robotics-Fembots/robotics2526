from tkinter import *
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import pygetwindow as gw
import pyscreeze
import keyboard
import threading
import time

width, height = 1300, 1100

#assign the cams
#cam1 = cv2.VideoCapture(0)
cam1 = cv2.VideoCapture('http://192.168.1.99:8080/stream')
cam1.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam1.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

#cam2 = cv2.VideoCapture(0)
cam2 = cv2.VideoCapture('http://192.168.1.99:8084/stream')
cam2.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam2.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# create first window
displayTop = Tk()
displayTop.title('top photosphere')
displayTop.bind('<Escape>', lambda e: displayTop.quit())

# create camera display 
cam1Display = Label(displayTop)
cam1Display.pack()

# create second window
def new_window():
    print("Opening new window")
    global cam2Display
    check = False  

    # create second window
    displayBottom = tk.Toplevel()
    displayBottom.title('bottom photosphere')
    displayBottom.bind('<Escape>', lambda e: displayBottom.quit())

    # create camera display
    cam2Display = Label(displayBottom)
    cam2Display.pack()
    print("Made second display")

    check = True
    if check:
        # start camera update functions
        update_camera1() 
        update_camera2()  

# runs first cam stream and keeps updating the display
def update_camera1():
    ret, frame1 = cam1.read()
    if ret:
        opencv_image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGBA)
        captured_image1 = Image.fromarray(opencv_image1)
        photo_image1 = ImageTk.PhotoImage(image=captured_image1)
        cam1Display.photo_image1 = photo_image1
        cam1Display.configure(image=photo_image1)
    displayTop.after(20, update_camera1)  # updates next frame

# runs second cam stream and keeps updating the display
def update_camera2():
    ret2, frame2 = cam2.read()
    if ret2:
        opencv_image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGBA)
        captured_image2 = Image.fromarray(opencv_image2)
        photo_image2 = ImageTk.PhotoImage(image=captured_image2)
        cam2Display.photo_image2 = photo_image2
        cam2Display.configure(image=photo_image2)
    displayTop.after(20, update_camera2)  #updates next frame

# screenshots
def screenshot():
    counter = 0
    while True:
        if keyboard.is_pressed("p"): 
            counter += 1
            timestamp = time.strftime("%Y%m%d_%H%M%S") #gets time for file saving

            windowTop = gw.getWindowsWithTitle('Top Photosphere')[0]
            windowBottom = gw.getWindowsWithTitle('Bottom Photosphere')[0]

            if windowTop and windowBottom:
                frameTop = pyscreeze.screenshot(region=windowTop.box)
                frameTop = frameTop.crop((20, 62, 1287, 1081))
                frameTop.save(f'C:/Users/SFHSR/OneDrive/Desktop/videoframes/savedTop_{timestamp}_{counter}.png')
                frameTop.show()

                frameBottom = pyscreeze.screenshot(region=windowBottom.box)
                frameBottom = frameBottom.crop((20, 64, 1290, 1082))
                frameBottom.save(f'C:/Users/SFHSR/OneDrive/Desktop/videoframes/savedBottom_{timestamp}_{counter}.png')
                frameBottom.show()

                print(f"Saved screenshot {counter}")
        time.sleep(0.1) 

# button to open cams
openButton = Button(displayTop, text="Open cams", command=new_window)
openButton.pack()

# screenshot thread
screenshotThread = threading.Thread(target=screenshot, daemon=True)
screenshotThread.start()

# run first window
displayTop.mainloop()