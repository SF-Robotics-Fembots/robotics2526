# import the require packages.
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, \
    QLabel, QGridLayout, QScrollArea, QSizePolicy, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QEvent, QObject
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import sys
import time
from PyQt5 import *
from PyQt5 import QtWidgets
import cv2
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import numpy as np
from tkinter import *
import tkinter as tk
import pyautogui as pg
import time
import pygetwindow
from PIL import Image, ImageTk
import pyscreeze
import keyboard

class ScreenshotThread(QThread):
    screenshot_taken = pyqtSignal(str)

    def __init__(self):
        super().__init__()
    
    def run(self):
        keyboard.on_press_key("t", lambda _: self.screenshottop())
        keyboard.on_press_key("m", lambda _: self.screenshotmiddle())
        keyboard.on_press_key("b", lambda _: self.screenshotbottom())
        while True:
            time.sleep(0.1)
        '''while True:
            if keyboard.is_pressed('p'):
                print("got pressed")
                self.screenshot()
                time.sleep(0.01)'''
    
    def screenshottop(self):
        print("taking screenshot")
        random = time.strftime("%Y%m%d_%H%M%S")
        file = "D:/screenshots" + str(random) + ".png"
        window = pygetwindow.getWindowsWithTitle('CAMERA GUI')[0]
        pg = pyscreeze.screenshot(region=window.box)
        #pg.show()
        #pg.screenshot(f'C:/Users/SFHSR/OneDrive/Desktop/videoframes/savedBottom_{random}.png')

        '''dimensions for ops laptop'''
        top = pg.crop((12, 46, 836, 734))
        top.save(f'C:/Users/SFHSR/OneDrive/Desktop/screenshots/savedTop_{random}.png')
        #top.show()
        #middle.show()
        #bottom.show()


        self.screenshot_taken.emit(file)

    def screenshotbottom(self):             
        print("taking screenshot")
        random = time.strftime("%Y%m%d_%H%M%S")
        file = "D:/screenshots" + str(random) + ".png"
        window = pygetwindow.getWindowsWithTitle('CAMERA GUI')[0]
        pg = pyscreeze.screenshot(region=window.box)
        #pg.show()
        #pg.screenshot(f'C:/Users/SFHSR/OneDrive/Desktop/videoframes/savedBottom_{random}.png')

        '''dimensions for ops laptop'''
        bottom = pg.crop((1688, 46, 2510, 734))
        bottom.save(f'C:/Users/SFHSR/OneDrive/Desktop/screenshots/savedBottom_{random}.png')
        #top.show()
        #middle.show()
        #bottom.show()


        self.screenshot_taken.emit(file)

    def screenshotmiddle(self):
        print("taking screenshot")
        random = time.strftime("%Y%m%d_%H%M%S")
        file = "D:/screenshots" + str(random) + ".png"
        window = pygetwindow.getWindowsWithTitle('CAMERA GUI')[0]
        pg = pyscreeze.screenshot(region=window.box)
        #pg.show()
        #pg.screenshot(f'C:/Users/SFHSR/OneDrive/Desktop/videoframes/savedBottom_{random}.png')

        '''dimensions for ops laptop'''
        middle = pg.crop((850, 46, 1674, 734))
        middle.save(f'C:/Users/SFHSR/OneDrive/Desktop/screenshots/savedMiddle_{random}.png')
        #top.show()
        #middle.show()
        #bottom.show()


        self.screenshot_taken.emit(file)



#gets camera frames
class CaptureCam(QThread):


    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, url):
        super(CaptureCam, self).__init__()
        self.url = url
        self.threadActive = True

    def run(self) -> None:
        capture = cv2.VideoCapture(self.url)

        if capture.isOpened():
            while self.threadActive:
                #
                ret, frame = capture.read()
                #rotating cameras
                #if self.url == 'http://192.168.1.99:8086/stream':
                #    frame = cv2.rotate(frame, cv2.ROTATE_180)
                # frame setup
                if ret:
                    height, width, channels = frame.shape
                    bytes_per_line = width * channels
                    cv_rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    qt_rgb_image_scaled = qt_rgb_image.scaled(520, 480, Qt.KeepAspectRatio)

                    self.ImageUpdate.emit(qt_rgb_image_scaled)
                else:
                    break
        capture.release()
        self.quit()

    def stop(self) -> None:
        self.threadActive = False

#ui setup
class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        self.screenshot_thread = ScreenshotThread()

        self.screenshot_thread.screenshot_taken.connect(self.on_screenshot_taken)

        self.screenshot_thread.start()

        #get camera streams
        self.url_1 = 'http://192.168.1.99:8082/stream' #top
        self.url_2 = "http://192.168.1.99:8086/stream" #nav
        self.url_3 = "http://192.168.1.99:8084/stream" #back gripper

        #self.url_1 = 0
        #self.url_2 = 0
        #self.url_3 = 0
        #self.url_4 = 0

        self.list_cameras = {}

        self.camera_1 = QLabel()
        self.camera_1.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_1.setScaledContents(True)
        self.camera_1.installEventFilter(self)
        self.camera_1.setObjectName("Camera_1")
        self.list_cameras["Camera_1"] = "Normal"

        self.QScrollArea_1 = QScrollArea()
        self.QScrollArea_1.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_1.setWidgetResizable(True)
        self.QScrollArea_1.setWidget(self.camera_1)

        
        self.camera_2 = QLabel()
        self.camera_2.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_2.setScaledContents(True)
        self.camera_2.installEventFilter(self)
        self.camera_2.setObjectName("Camera_2")
        self.list_cameras["Camera_2"] = "Normal"

        self.QScrollArea_2 = QScrollArea()
        self.QScrollArea_2.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_2.setWidgetResizable(True)
        self.QScrollArea_2.setWidget(self.camera_2)

    
        self.camera_3 = QLabel()
        self.camera_3.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_3.setScaledContents(True)
        self.camera_3.installEventFilter(self)
        self.camera_3.setObjectName("Camera_3")
        self.list_cameras["Camera_3"] = "Normal"

        self.QScrollArea_3 = QScrollArea()
        self.QScrollArea_3.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_3.setWidgetResizable(True)
        self.QScrollArea_3.setWidget(self.camera_3)

        self.camera1_label = QLabel("bottom photosphere", self)
        self.camera1_label.setStyleSheet("color: #F1F6FD")
        self.camera1_label.setAlignment(Qt.AlignCenter)
        self.camera2_label = QLabel("nav", self)
        self.camera2_label.setStyleSheet("color: #F1F6FD")
        self.camera2_label.setAlignment(Qt.AlignCenter)
        self.camera3_label = QLabel("top photosphere", self)
        self.camera3_label.setStyleSheet("color: #F1F6FD")
        self.camera3_label.setAlignment(Qt.AlignCenter)

        self.__SetupUI()

        #connects to ImageUpdate to keep updating the frames
        self.CaptureCam_1 = CaptureCam(self.url_1)
        self.CaptureCam_1.ImageUpdate.connect(lambda image: self.ShowCamera1(image))

        self.CaptureCam_2 = CaptureCam(self.url_2)
        self.CaptureCam_2.ImageUpdate.connect(lambda image: self.ShowCamera2(image))

        self.CaptureCam_3 = CaptureCam(self.url_3)
        self.CaptureCam_3.ImageUpdate.connect(lambda image: self.ShowCamera3(image))

        #.start() runs the .run() function in CaptureCam that changes frame settings
        self.CaptureCam_1.start()
        self.CaptureCam_2.start()
        self.CaptureCam_3.start()

        #self.start_key_press_listener()

    def __SetupUI(self):
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(self.QScrollArea_1, 0, 0)
        grid_layout.addWidget(self.QScrollArea_2, 0, 1)
        grid_layout.addWidget(self.QScrollArea_3, 0, 2)
        grid_layout.addWidget(self.camera1_label, 1, 0)
        grid_layout.addWidget(self.camera2_label, 1, 1)
        grid_layout.addWidget(self.camera3_label, 1, 2)


        self.widget = QWidget(self)
        self.widget.setLayout(grid_layout)

        self.setCentralWidget(self.widget)
        self.setMinimumSize(2500, 720)
        #self.showMaximized()
        self.setStyleSheet("QMainWindow {background: 'midnightblue';}")

        self.setWindowTitle("CAMERA GUI")

    @QtCore.pyqtSlot()
    def ShowCamera1(self, frame: QImage) -> None:
        self.camera_1.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera2(self, frame: QImage) -> None:
        self.camera_2.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera3(self, frame: QImage) -> None:
        self.camera_3.setPixmap(QPixmap.fromImage(frame))

    def start_key_press_listener(self):
        self.listener_thread = QThread(target=self.start_key_press_listener)
        self.listener_thread.start()

    def on_screenshot_taken(self):
        print("Screenshot saved")

    def switch(self):
        random = int(time.time())
        file = "D:/screenshots" + str(random) + ".png"
        window = pygetwindow.getWindowsWithTitle('CAMERA GUI')[0]
        pg.screenshot(file)
        im = file
        #im = im.crop((, , , ))
        im.save(file)
        #im.show(file)

    def close(self, event):
        if self.CaptureCam_1.isRunning():
            self.CaptureCam_1.quit()
        if self.CaptureCam_2.isRunning():
            self.CaptureCam_2.quit()
        if self.CaptureCam_3.isRunning():
            self.CaptureCam_3.quit()
        event.accept()


#runs window
def main():
    # Create a QApplication object. It manages the GUI application's control flow and main settings.
    # It handles widget specific initialization, finalization.
    # For any GUI application using Qt, there is precisely one QApplication object
    app = QApplication(sys.argv)
    # Create an instance of the class MainWindow.
    window = MainWindow()
    # Show the window.
    window.show()
    # Start Qt event loop.
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()