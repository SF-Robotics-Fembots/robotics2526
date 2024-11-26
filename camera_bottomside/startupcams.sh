#!/bin/bash

rmmod uvcvideo
modprobe uvcvideo nodrop=1 timeout=5000 quirks=0x80
bash focusscript.sh
bash /home/geneseas/robotics2425/camerarun.sh 0 & sleep 5 
bash /home/geneseas/robotics2425/camerarun.sh 2 & sleep 5 
bash /home/geneseas/robotics2425/camerarun.sh 4 & sleep 5 
bash /home/geneseas/robotics2425/camerarun.sh 6 & sleep 5
bash /home/geneseas/robotics2425/camerarun.sh 8 & sleep 5
bash /home/geneseas/robotics2425/camerarun.sh 1 & sleep 5 