#!/usr/bin/env python3
import serial
import time

PORT1 = "/dev/ttyAMA0"
PORT2 = "/dev/ttyAMA10"
BAUD  = 19200

LASER_ON  = b'\xAA\x00\x01\xBE\x00\x01\x00\x01\xC1'
LASER_OFF = b'\xAA\x00\x01\xBE\x00\x01\x00\x00\xC0'
STOP_CONT = b'\x58'

# ----------------------------
# Connect
# ----------------------------
print(f"Connecting to laser 1 on {PORT1}...")
laser1 = serial.Serial(port=PORT1, baudrate=BAUD, timeout=0.5)
print(f"Connecting to laser 2 on {PORT2}...")
laser2 = serial.Serial(port=PORT2, baudrate=BAUD, timeout=0.5)
print("Both lasers connected.")

# Stop any continuous mode
for l in (laser1, laser2):
    l.write(STOP_CONT)
    time.sleep(0.1)

# ----------------------------
# Control functions
# ----------------------------
def laser_on():
    laser1.write(LASER_ON)
    laser2.write(LASER_ON)
    print("Lasers ON")

def laser_off():
    laser1.write(LASER_OFF)
    laser2.write(LASER_OFF)
    print("Lasers OFF")

# ----------------------------
# Main loop
# ----------------------------
print("\nCommands: 'on', 'off', 'quit'")
try:
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "on":
            laser_on()
        elif cmd == "off":
            laser_off()
        elif cmd in ("quit", "q"):
            break
        else:
            print("Unknown command. Use: on, off, quit")
except KeyboardInterrupt:
    pass

# ----------------------------
# Cleanup
# ----------------------------
laser_off()
laser1.close()
laser2.close()
print("Exited safely")