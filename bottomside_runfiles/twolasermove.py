#!/usr/bin/env python3

import serial
import serial.tools.list_ports
import time
import sys
import cv2

# ----------------------------
# Select TWO laser ports
# ----------------------------
ports = list(serial.tools.list_ports.comports())

if len(ports) < 2:
    print("Need at least TWO serial devices")
    sys.exit(1)

print("Available serial devices:")
for i, p in enumerate(ports):
    print(f"{i}) {p.device} | {p.description}")

try:
    i1 = int(input("\nSelect FIRST laser port: "))
    i2 = int(input("Select SECOND laser port: "))
    port1 = ports[i1].device
    port2 = ports[i2].device
except:
    print("Invalid selection")
    sys.exit(1)

# ----------------------------
# Open connections
# ----------------------------
def open_laser(port):
    return serial.Serial(port=port, baudrate=19200, timeout=0.5)

laser1 = open_laser(port1)
laser2 = open_laser(port2)

# ----------------------------
# Commands
# ----------------------------
LASER_ON  = b'\xAA\x00\x01\xBE\x00\x01\x00\x01\xC1'
LASER_OFF = b'\xAA\x00\x01\xBE\x00\x01\x00\x00\xC0'
MEASURE   = b'\xAA\x00\x00\x20\x00\x01\x00\x00\x21'
STOP_CONT = b'\x58'

for l in (laser1, laser2):
    l.write(STOP_CONT)
    time.sleep(0.1)

def laser_on():
    laser1.write(LASER_ON)
    laser2.write(LASER_ON)

def laser_off():
    laser1.write(LASER_OFF)
    laser2.write(LASER_OFF)

def get_distance(laser):
    laser.reset_input_buffer()
    laser.write(MEASURE)

    data = laser.readline()
    while len(data) < 10:
        data = laser.readline()

    if data[0] == 0xEE:
        return None

    return int.from_bytes(data[6:10], "big")

# ----------------------------
# CAMERA DISPLAY
# ----------------------------
cap = cv2.VideoCapture(0)

laser_on()

print("\nPress 'q' to quit\n")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        d1 = get_distance(laser1)
        d2 = get_distance(laser2)

        # Text to display
        text1 = f"Laser 1: {d1} mm" if d1 else "Laser 1: ERROR"
        text2 = f"Laser 2: {d2} mm" if d2 else "Laser 2: ERROR"

        # Draw on screen
        cv2.putText(frame, text1, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.putText(frame, text2, (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        if d1 and d2:
            diff = abs(d1 - d2)
            cv2.putText(frame, f"Diff: {diff} mm", (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow("Laser Measurement", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

# ----------------------------
# Cleanup
# ----------------------------
laser_off()
laser1.close()
laser2.close()
cap.release()
cv2.destroyAllWindows()

print("Exited safely")