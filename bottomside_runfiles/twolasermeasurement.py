import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# --- GPIO SETUP (for lasers) ---
LASER1 = 17
LASER2 = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(LASER1, GPIO.OUT)
GPIO.setup(LASER2, GPIO.OUT)

def lasers_on():
    GPIO.output(LASER1, True)
    GPIO.output(LASER2, True)

def lasers_off():
    GPIO.output(LASER1, False)
    GPIO.output(LASER2, False)

# --- CALIBRATION ---
REAL_DISTANCE_BETWEEN_LASERS = 10.0  # cm (measure this physically)
PIXELS_PER_CM = 20  # adjust after calibration

# --- DETECT LASER POINTS ---
def find_laser_points(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # detect green lasers
    lower = np.array([40, 100, 100])
    upper = np.array([80, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)

    points = cv2.findNonZero(mask)
    if points is None:
        return None

    x, y, w, h = cv2.boundingRect(points)
    return (x + w//2, y + h//2)

# --- MAIN MEASUREMENT ---
cap = cv2.VideoCapture(0)

lasers_on()
time.sleep(1)  # allow camera to adjust

ret, frame = cap.read()

point = find_laser_points(frame)

if point:
    # assume two bright spots → split image
    h, w, _ = frame.shape
    left = frame[:, :w//2]
    right = frame[:, w//2:]

    p1 = find_laser_points(left)
    p2 = find_laser_points(right)

    if p1 and p2:
        # adjust p2 x position since it's from right half
        p2 = (p2[0] + w//2, p2[1])

        pixel_dist = abs(p2[0] - p1[0])
        real_width = pixel_dist / PIXELS_PER_CM

        print(f"Measured width: {real_width:.2f} cm")

lasers_off()
cap.release()
GPIO.cleanup()