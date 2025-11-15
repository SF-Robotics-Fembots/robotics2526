#!/bin/bash

#bash cameraon.sh
#camera on by default 
#rmmod uvcvideo
#modprobe uvcvideo nodrop=1 timeout=5000 quirks=0x80
bash /home/geneseas/robotics2425/camera_bottomside/focusscript.sh
bash /home/geneseas/robotics2425/camera_bottomside/camerarun.sh 0 & sleep 3 
bash /home/geneseas/robotics2425/camera_bottomside/camerarun.sh 2 & sleep 3 
bash /home/geneseas/robotics2425/camera_bottomside/camerarun.sh 4 & sleep 3 
#bash /home/geneseas/robotics2425/camera_bottomside/camerarun.sh 6 & sleep 3
#bash /home/geneseas/robotics2425/camera_bottomside/camerarun.sh 8 & sleep 3
#/home/geneseas/ustreamer/ustreamer --device=/dev/video10 --host=192.168.1.99 --format=MJPEG --port=8090 --device-timeout 2 -r 800x600 -b 2 --workers 2 --encoder=HW
