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
$GPIO_PATH 0x0424 0x$PID 0x01 3 1
$GPIO_PATH 0x0424 0x$PID 0x01 7 0
$GPIO_PATH 0x0424 0x$PID 0x01 9 1


# ======== EXACT startupcams.sh BELOW ========

#bash cameraon.sh
#camera on by default
#rmmod uvcvideo
#modprobe uvcvideo nodrop=1 timeout=5000 quirks=0x80
bash /home/geneseas/robotics2526/camera_bottomside/focusscript.sh
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 0 & sleep 3
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 2 & sleep 3
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 4 & sleep 3
# bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 6 & sleep 3
# bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 8 & sleep 3
#/home/geneseas/ustreamer/ustreamer --device=/dev/video10 --host=192.168.1.99 --format=MJPEG --port=8090 --device-timeout 2 -r 800x600 -b 2 --workers 2 --e>
#!/usr/bin/bash

GPIO_PATH="/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio"

# Grab PID dynamically
PID=$(lsusb | grep 'USB2734' | awk '{print $6}' | cut -d: -f2)

if [ -z "$PID" ]; then
    echo "USB2734 hub not found."
    exit 1
fi

echo "Detected PID: $PID"

$GPIO_PATH 0x0424 0x$PID 0x01 2 0
$GPIO_PATH 0x0424 0x$PID 0x01 3 1
$GPIO_PATH 0x0424 0x$PID 0x01 7 0
$GPIO_PATH 0x0424 0x$PID 0x01 9 1
\#!/usr/bin/bash
#making a new bash script to run the camera GPIOs
/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio 0x0424 0x2732 0x01 2 0
/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio 0x0424 0x2732 0x01 3 1
/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio 0x0424 0x2732 0x01 7 0
/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio 0x0424 0x2732 0x01 9 1
