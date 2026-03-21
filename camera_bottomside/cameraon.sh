#!/usr/bin/bash

GPIO_PATH="/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio"

echo "Searching for USB2734 hub..."

PID=$(lsusb | grep 'USB2734' | awk '{print $6}' | cut -d: -f2)

if [ -z "$PID" ]; then
    echo "ERROR: USB2734 hub not found."
    exit 1
fi

echo "Detected PID: $PID"

$GPIO_PATH 0x0424 0x$PID 0x01 2 0
sleep 3
$GPIO_PATH 0x0424 0x$PID 0x01 3 1
sleep 3
$GPIO_PATH 0x0424 0x$PID 0x01 7 0
sleep 3
$GPIO_PATH 0x0424 0x$PID 0x01 9 1


