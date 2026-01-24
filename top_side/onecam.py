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
import keyboard
from PIL import Image
import pygame

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
                #read frames
                ret, frame = capture.read()

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

        #get camera streams
        #self.url_1 = 0
        self.url_1 = 'http://192.168.1.99:8080/stream'
        self.url_2 = "http://192.168.1.99:8082/stream"
        #self.url_2 = 1
        self.url_3 = "http://192.168.1.99:8084/stream"
        #self.url_4 = "http://192.168.1.99:8086/stream" #photogrammetry cam
        #self.url_5 =  "http://192.168.1.99:8088/stream"
        #self.url_6 = "http://192.168.1.99:8090/stream"

        #self.url_1 = 0
        #self.url_2 = 0
        #self.url_3 = 0
        #self.url_4 = 0

        self.list_cameras = {}
        self.cams_stream = [self.url_1, self.url_2, self.url_3]
        #self.cams_stream = [self.url_1, self.url_2, self.url_3, self.url_4, self.url_5, self.url_6]
        #self.camera = self.url_1
        self.index = 0

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

        self.camera1_label = QLabel("un", self)
        self.camera1_label.setStyleSheet("color: #F1F6FD")
        self.camera1_label.setAlignment(Qt.AlignCenter)

        #setup UI call
        self.__SetupUI()

        #connects to ImageUpdate to keep updating the frames
        self.CaptureCam_1 = CaptureCam(self.cams_stream[self.index])
        self.CaptureCam_1.ImageUpdate.connect(lambda image: self.ShowCamera1(image))

        #.start() runs the .run() function in CaptureCam that changes frame settings
        self.CaptureCam_1.start()
            
    def __SetupUI(self):
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(self.QScrollArea_1, 0, 0)
        grid_layout.addWidget(self.camera1_label, 1, 0)


        self.widget = QWidget(self)
        self.widget.setLayout(grid_layout)

        self.setCentralWidget(self.widget)
        self.setMinimumSize(1570, 1440)
        #self.showMaximized()
        self.setStyleSheet("QMainWindow {background: 'midnightblue';}")

        self.setWindowTitle("CAMERA GUI")

    @QtCore.pyqtSlot()
    def ShowCamera1(self, frame: QImage) -> None:
        self.camera_1.setPixmap(QPixmap.fromImage(frame))

    def eventFilter(self, source: QObject, event: QEvent):
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            print("double click")
            self.index = (self.index + 1) % len(self.cams_stream)
            print(self.cams_stream[self.index])
            self.CaptureCam_1.stop()
            self.CaptureCam_1 = CaptureCam(self.cams_stream[self.index])
            self.CaptureCam_1.ImageUpdate.connect(lambda image: self.ShowCamera1(image))
            self.CaptureCam_1.start()
            print(self.index)
            return True
        else:
            return super(MainWindow, self).eventFilter(source, event)
    
    def close(self, event):
        if self.CaptureCam_1.isRunning():
            self.CaptureCam_1.quit()
        event.accept()


#runs window
def main():
    # Create a QApplication object. It manages the GUI application's control flow and main settings.
    # It handles widget specific initialization, finalization.
    # For any GUI application using Qt, there is precisely one QApplication object
    app = QApplication(sys.argv)
    print("start cam")
    # Create an instance of the class MainWindow.
    window = MainWindow()
    # Show the window.
    window.show()
    # Start Qt event loop.
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()