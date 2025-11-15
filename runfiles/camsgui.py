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
from PIL import Image
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
                if self.url == 'http://192.168.1.99:8080/stream':
                    frame = cv2.rotate(frame, cv2.ROTATE_180)
                #if self.url == "http://192.168.1.99:8082/stream":
                #    frame = cv2.rotate(frame, cv2.ROTATE_180)
                #if self.url == "http://192.168.1.99:8088/stream":
                #    frame = cv2.rotate(frame, cv2.ROTATE_180)
                # frame setupsss
                if ret:
                    height, width, channels = frame.shape
                    bytes_per_line = width * channels
                    cv_rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    qt_rgb_image_scaled = qt_rgb_image.scaled(520, 480, Qt.KeepAspectRatio)


                    self.ImageUpdate.emit(qt_rgb_image_scaled)
                else:
                    break
                time.sleep(0.015)
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
        #self.url_2 = 1
        self.url_1 = 'http://192.168.1.99:8082/stream' #nav
        self.url_2 = "http://192.168.1.99:8080/stream" #top
        self.url_3 = "http://192.168.1.99:8084/stream" #bottom
        self.url_4 = "http://192.168.1.99:8086/stream" #gripper back
        self.url_5 =  "http://192.168.1.99:8088/stream"
        self.url_6 = "http://192.168.1.99:8090/stream"


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




        self.camera_4 = QLabel()
        self.camera_4.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_4.setScaledContents(True)
        self.camera_4.installEventFilter(self)
        self.camera_4.setObjectName("Camera_4")
        self.list_cameras["Camera_4"] = "Normal"


        self.QScrollArea_4 = QScrollArea()
        self.QScrollArea_4.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_4.setWidgetResizable(True)
        self.QScrollArea_4.setWidget(self.camera_4)


        self.camera_5 = QLabel()
        self.camera_5.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_5.setScaledContents(True)
        self.camera_5.installEventFilter(self)
        self.camera_5.setObjectName("Camera_5")
        self.list_cameras["Camera_5"] = "Normal"


        self.QScrollArea_5 = QScrollArea()
        self.QScrollArea_5.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_5.setWidgetResizable(True)
        self.QScrollArea_5.setWidget(self.camera_5)


        self.camera_6 = QLabel()
        self.camera_6.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_6.setScaledContents(True)
        self.camera_6.installEventFilter(self)
        self.camera_6.setObjectName("Camera_6")
        self.list_cameras["Camera_6"] = "Normal"


        self.QScrollArea_6 = QScrollArea()
        self.QScrollArea_6.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_6.setWidgetResizable(True)
        self.QScrollArea_6.setWidget(self.camera_6)


        self.camera1_label = QLabel("back photosphere ♡", self)
        self.camera1_label.setStyleSheet("color: white")
        self.camera1_label.setAlignment(Qt.AlignCenter)
        self.camera2_label = QLabel("back gripper ୨ৎ", self)
        self.camera2_label.setStyleSheet("color: white")
        self.camera2_label.setAlignment(Qt.AlignCenter)
        self.camera3_label = QLabel("top photosphere ♡", self)
        self.camera3_label.setStyleSheet("color: white")
        self.camera3_label.setAlignment(Qt.AlignCenter)
        self.camera4_label = QLabel("nav cam ❀", self)
        self.camera4_label.setStyleSheet("color: white")
        self.camera4_label.setAlignment(Qt.AlignCenter)
        self.camera5_label = QLabel("front gripper ୨ৎ", self)
        self.camera5_label.setStyleSheet("color: white")
        self.camera5_label.setAlignment(Qt.AlignCenter)
        self.camera6_label = QLabel("tools cam ❀", self)
        self.camera6_label.setStyleSheet("color: white")
        self.camera6_label.setAlignment(Qt.AlignCenter)


        self.__SetupUI()


        #connects to ImageUpdate to keep updating the frames
        self.CaptureCam_1 = CaptureCam(self.url_1)
        self.CaptureCam_1.ImageUpdate.connect(lambda image: self.ShowCamera1(image))


        self.CaptureCam_2 = CaptureCam(self.url_2)
        self.CaptureCam_2.ImageUpdate.connect(lambda image: self.ShowCamera2(image))


        self.CaptureCam_3 = CaptureCam(self.url_3)
        self.CaptureCam_3.ImageUpdate.connect(lambda image: self.ShowCamera3(image))


        self.CaptureCam_4 = CaptureCam(self.url_4)
        self.CaptureCam_4.ImageUpdate.connect(lambda image: self.ShowCamera4(image))


        self.CaptureCam_5 = CaptureCam(self.url_5)
        self.CaptureCam_5.ImageUpdate.connect(lambda image: self.ShowCamera5(image))


        self.CaptureCam_6 = CaptureCam(self.url_6)
        self.CaptureCam_6.ImageUpdate.connect(lambda image: self.ShowCamera6(image))


        #.start() runs the .run() function in CaptureCam that changes frame settings
        self.CaptureCam_1.start()
        self.CaptureCam_2.start()
        self.CaptureCam_3.start()
        self.CaptureCam_4.start()
        self.CaptureCam_5.start()
        self.CaptureCam_6.start()


    def __SetupUI(self):
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(self.QScrollArea_1, 0, 0)
        grid_layout.addWidget(self.QScrollArea_2, 0, 1)
        grid_layout.addWidget(self.QScrollArea_3, 0, 2)
        grid_layout.addWidget(self.camera1_label, 1, 0)
        grid_layout.addWidget(self.camera2_label, 1, 1)
        grid_layout.addWidget(self.camera3_label, 1, 2)
        grid_layout.addWidget(self.QScrollArea_4, 2, 0)
        grid_layout.addWidget(self.QScrollArea_5, 2, 1)
        grid_layout.addWidget(self.QScrollArea_6, 2, 2)
        grid_layout.addWidget(self.camera4_label, 3, 0)
        grid_layout.addWidget(self.camera5_label, 3, 1)
        grid_layout.addWidget(self.camera6_label, 3, 2)


        self.widget = QWidget(self)
        self.widget.setLayout(grid_layout)


        self.setCentralWidget(self.widget)
        self.setMinimumSize(1570, 1440)
        #self.showMaximized()
        self.setStyleSheet("QMainWindow {background: 'lightblue';}")


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


    @QtCore.pyqtSlot()
    def ShowCamera4(self, frame: QImage) -> None:
        self.camera_4.setPixmap(QPixmap.fromImage(frame))


    @QtCore.pyqtSlot()
    def ShowCamera5(self, frame: QImage) -> None:
        self.camera_5.setPixmap(QPixmap.fromImage(frame))


    @QtCore.pyqtSlot()
    def ShowCamera6(self, frame: QImage) -> None:
        self.camera_6.setPixmap(QPixmap.fromImage(frame))


#runs window
def main():
    # Create a QApplication object. It manages the GUI application's control flow and main settings.
    # It handles widget specific initialization, finalization.
    # For any GUI application using Qt, there is precisely one QApplication object
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica", 14, QFont.Bold))
    # Create an instance of the class MainWindow.
    window = MainWindow()
    # Show the window.
    window.show()
    # Start Qt event loop.
    sys.exit(app.exec_())
   




if __name__ == '__main__':
    main()

