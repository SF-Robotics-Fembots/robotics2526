#!/usr/bin/env python3
import serial
import serial.tools.list_ports
import time
import sys
import lgpio

LASER_GPIO = 23

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

print("hello")
# ----------------------------
# Open connections
# ----------------------------
def open_laser(port):
    return serial.Serial(port=port, baudrate=19200, timeout=0.5)

laser1 = open_laser(port1)
laser2 = open_laser(port2)

print("hiii")
# ----------------------------
# Commands
# ----------------------------
LASER_ON  = b'\xAA\x00\x01\xBE\x00\x01\x00\x01\xC1'
LASER_OFF = b'\xAA\x00\x01\xBE\x00\x01\x00\x00\xC0'
STOP_CONT = b'\x58'

for l in (laser1, laser2):
    l.write(STOP_CONT)
    time.sleep(0.1)

def laser_on():
    laser1.write(LASER_ON)
    laser2.write(LASER_ON)
    print("Lasers ON")

def laser_off():
    laser1.write(LASER_OFF)
    laser2.write(LASER_OFF)
    print("Lasers OFF")

print("lasers are dumb")
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

print("woiefjowiejf")
# ----------------------------
# Cleanup
# ----------------------------
laser_off()
laser1.close()
laser2.close()
print("Exited safely")