#i changed camera switching for screenshot
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QGridLayout, QScrollArea, QSizePolicy,
    QPushButton, QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import sys
import time
import os
import numpy as np


# --- Camera capture thread ---
class CaptureCam(QThread):
    ImageUpdate = pyqtSignal(QImage)
    RawFrameUpdate = pyqtSignal(object)

    def __init__(self, url, high_res=False):
        super().__init__()
        self.url = url
        self.high_res = high_res
        self.threadActive = True
        self.last_qt_image = None

    def run(self):
        capture = cv2.VideoCapture(self.url)

        if capture is None or not capture.isOpened():
            placeholder = self.create_placeholder()
            qt_img = self.cv_to_qt(placeholder)
            while self.threadActive:
                self.ImageUpdate.emit(qt_img)
                time.sleep(0.5)
            return

        while self.threadActive:
            ret, frame = capture.read()
            if not ret:
                placeholder = self.create_placeholder()
                qt_img = self.cv_to_qt(placeholder)
                self.ImageUpdate.emit(qt_img)
                time.sleep(0.5)
                continue

            if self.url == 'http://192.168.1.68:8080/stream':
                frame = cv2.rotate(frame, cv2.ROTATE_180)

            cv_rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = cv_rgb_image.shape
            bytes_per_line = width * channels

            if self.high_res:
                self.RawFrameUpdate.emit(cv_rgb_image)

            qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            qt_rgb_image_scaled = qt_rgb_image.scaled(520, 480, Qt.KeepAspectRatio)
            self.ImageUpdate.emit(qt_rgb_image_scaled)

            time.sleep(0.01)

        capture.release()
        self.quit()

    def cv_to_qt(self, frame):
        h, w, c = frame.shape
        bytes_per_line = c * w
        qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return qt_img.scaled(520, 480, Qt.KeepAspectRatio)

    def create_placeholder(self):
        img = np.ones((480, 640, 3), dtype=np.uint8) * 255
        img[:] = [255, 232, 240]

        offline_text = "CAMERA OFFLINE"
        text_scale = 2
        text_thickness = 4
        text_size = cv2.getTextSize(offline_text, cv2.FONT_HERSHEY_SIMPLEX, text_scale, text_thickness)[0]
        text_x = (img.shape[1] - text_size[0]) // 2
        text_y = (img.shape[0] + text_size[1]) // 2

        cv2.putText(img, offline_text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    text_scale, (255, 0, 128),
                    text_thickness, cv2.LINE_AA)

        return img

    def stop(self):
        self.threadActive = False


# --- Screenshot window ---
class ScreenshotWindow(QMainWindow):
    def __init__(self, camera_threads):
        super().__init__()

        self.camera_threads = camera_threads
        self.current_index = 1
        self.current_frame_cv = None
        self.last_qt_image = None

        self.setWindowTitle("← → to switch cameras | P to screenshot")
        self.showMaximized()

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)

        self.connect_camera(self.current_index)

    def connect_camera(self, index):
        for cam in self.camera_threads:
            try:
                cam.ImageUpdate.disconnect(self.update_image)
                cam.RawFrameUpdate.disconnect(self.store_raw_frame)
            except:
                pass

        cam = self.camera_threads[index]
        cam.ImageUpdate.connect(self.update_image)
        cam.RawFrameUpdate.connect(self.store_raw_frame)

    def store_raw_frame(self, frame):
        self.current_frame_cv = frame

    def update_image(self, qt_image):
        self.last_qt_image = qt_image

        pixmap = QPixmap.fromImage(qt_image)
        self.label.setPixmap(
            pixmap.scaled(
                self.label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.camera_threads)
            self.connect_camera(self.current_index)

        elif event.key() == Qt.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.camera_threads)
            self.connect_camera(self.current_index)

        elif event.key() == Qt.Key_P:
            if self.current_frame_cv is None:
                return

            save_path = r"D:\screenshot_test"
            os.makedirs(save_path, exist_ok=True)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(save_path, f"cam_{self.current_index+1}_{timestamp}.png")

            frame = self.current_frame_cv
            h, w, _ = frame.shape

            if w < 3840 or h < 2160:
                frame = cv2.resize(frame, (3840, 2160), interpolation=cv2.INTER_CUBIC)

            cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            print(f"Saved screenshot to {filename}")

            msg = QMessageBox()
            msg.setWindowTitle("Saved!")
            msg.setText(f"Screenshot saved:\n{filename}")
            msg.exec_()

    def resizeEvent(self, event):
        if self.last_qt_image is not None:
            self.update_image(self.last_qt_image)
        super().resizeEvent(event)


# --- Main GUI ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.urls = [
            'http://192.168.1.68:8080/stream',
            'http://192.168.1.68:8082/stream',
            'http://192.168.1.68:8084/stream',
            'http://192.168.1.68:8086/stream',
            'http://192.168.1.68:8088/stream',
            'http://192.168.1.68:8090/stream'
        ]

        self.cameras = {}
        self.scroll_areas = {}

        for i in range(6):
            cam_label = QLabel()
            cam_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            cam_label.setScaledContents(True)

            scroll_area = QScrollArea()
            scroll_area.setBackgroundRole(QPalette.Dark)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(cam_label)

            self.cameras[f"Camera_{i+1}"] = cam_label
            self.scroll_areas[f"Camera_{i+1}"] = scroll_area

        labels = [
            "back photosphere ♡",
            "back gripper ୨ৎ",
            "top photosphere ♡",
            "nav cam ❀",
            "front gripper ୨ৎ",
            "tools cam ❀"
        ]

        self.camera_labels = []
        for text in labels:
            label = QLabel(text)
            label.setStyleSheet("color: black")
            label.setAlignment(Qt.AlignCenter)
            self.camera_labels.append(label)

        self.screenshot_btn = QPushButton("Screenshot!")
        self.screenshot_btn.clicked.connect(self.open_screenshot_window)
        self.screenshot_btn.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffc0cb, stop:1 #ffffff
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff69b4, stop:1 #ffb6c1
                );
            }
        """)

        self.__SetupUI()

        self.cam_threads = []
        for i, url in enumerate(self.urls):
            high_res = (i == 1)
            cam_thread = CaptureCam(url, high_res=high_res)
            cam_thread.ImageUpdate.connect(lambda img, n=i+1: self.ShowCamera(n, img))
            cam_thread.start()
            self.cam_threads.append(cam_thread)

    def open_screenshot_window(self):
        self.screenshot_window = ScreenshotWindow(self.cam_threads)
        self.screenshot_window.show()

    def __SetupUI(self):
        grid_layout = QGridLayout()

        positions = [(0,0),(0,1),(0,2),(2,0),(2,1),(2,2)]
        label_positions = [(1,0),(1,1),(1,2),(3,0),(3,1),(3,2)]

        for i in range(6):
            grid_layout.addWidget(self.scroll_areas[f"Camera_{i+1}"], *positions[i])
            grid_layout.addWidget(self.camera_labels[i], *label_positions[i])

        grid_layout.addWidget(self.screenshot_btn, 4, 1)

        self.widget = QWidget()
        self.widget.setLayout(grid_layout)
        self.setCentralWidget(self.widget)

        self.widget.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #add8e6, stop:1 #ffffff
            );
        """)

        self.setMinimumSize(1570, 1440)
        self.setWindowTitle("CAMERA GUI")

    def ShowCamera(self, cam_number, frame):
        self.cameras[f"Camera_{cam_number}"].setPixmap(QPixmap.fromImage(frame))


# --- Run ---
def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica", 14, QFont.Bold))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
