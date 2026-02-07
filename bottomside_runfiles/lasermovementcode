#!/usr/bin/env python3

import serial
import serial.tools.list_ports
import time
import sys

# ----------------------------
# Find laser serial port
# ----------------------------
ports = list(serial.tools.list_ports.comports())

if not ports:
    print("No serial devices found")
    sys.exit(1)

print("Available serial devices:")
for i, p in enumerate(ports):
    print(f"{i}) {p.device} | {p.description}")

try:
    index = int(input("\nSelect laser port number: "))
    port = ports[index].device
except (ValueError, IndexError):
    print("nvalid selection")
    sys.exit(1)

# ----------------------------
# Open serial connection
# ----------------------------
try:
    laser = serial.Serial(
        port=port,
        baudrate=19200,
        timeout=0.5
    )
except Exception as e:
    print("Failed to open serial port:", e)
    sys.exit(1)

print(f"Connected to laser on {port}")

# ----------------------------
# Laser commands
# ----------------------------
LASER_ON  = b'\xAA\x00\x01\xBE\x00\x01\x00\x01\xC1'
LASER_OFF = b'\xAA\x00\x01\xBE\x00\x01\x00\x00\xC0'
MEASURE   = b'\xAA\x00\x00\x20\x00\x01\x00\x00\x21'
STOP_CONT = b'\x58'

laser.write(STOP_CONT)
time.sleep(0.1)

def laser_on():
    laser.write(LASER_ON)

def laser_off():
    laser.write(LASER_OFF)

def get_distance_mm():
    laser.reset_input_buffer()
    laser.write(MEASURE)

    data = laser.readline()
    while len(data) < 10:
        data = laser.readline()

    if data[0] == 0xEE:
        return None

    return int.from_bytes(data[6:10], "big")

# ----------------------------
# Main loop
# ----------------------------
print("\nLaser distance measurement started")
print("Press CTRL+C to stop\n")

laser_on()

try:
    while True:
        distance = get_distance_mm()
        if distance is not None:
            print(f"Distance A → B: {distance} mm")
        else:
            print("Measurement error")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStopping laser...")
    laser_off()
    laser.close()
    print("Exited safely")
