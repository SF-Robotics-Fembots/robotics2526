#!/bin/bash

<<<<<<< HEAD
bash cameraon.sh	

#ok lets see if this fixes the error!
# Kill any processes using cameras
sudo fuser -k /dev/video0
sudo fuser -k /dev/video2
sudo fuser -k /dev/video4
sudo fuser -k /dev/video6
sudo fuser -k /dev/video8
sudo fuser -k /dev/video10

#camera on by default  2/28 i added sudo
sudo rmmod uvcvideo
sudo modprobe uvcvideo nodrop=1 timeout=5000 quirks=0x80
read -p "Press Enter"
bash /home/geneseas/robotics2526/camera_bottomside/focusscript.sh
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 0 & sleep 3
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 2 & sleep 3
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 4 & sleep 3
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 6 & sleep 3
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 8 & sleep 3
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 10 & sleep 3
#/home/geneseas/ustreamer/ustreamer --device=/dev/video10 --host=192.168.1.68 --format=MJPEG --port=8090 --device-timeout 2 -r 800x600 -b 2 --workers 2 --encoder=HW

=======
#bash cameraon.sh
#camera on by default 
#rmmod uvcvideo
#modprobe uvcvideo nodrop=1 timeout=5000 quirks=0x80
bash /home/geneseas/robotics2526/camera_bottomside/focusscript.sh
bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 0 & sleep 3
# bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 2 & sleep 3
# bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 4 & sleep 3
# bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 6 & sleep 3
# bash /home/geneseas/robotics2526/camera_bottomside/camerarun.sh 8 & sleep 3
#/home/geneseas/ustreamer/ustreamer --device=/dev/video10 --host=192.168.1.99 --format=MJPEG --port=8090 --device-timeout 2 -r 800x600 -b 2 --workers 2 --encoder=HW
>>>>>>> cd47fe3e29a1e9faf496316214b3223db8e47bd8
