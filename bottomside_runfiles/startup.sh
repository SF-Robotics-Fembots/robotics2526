#!/bin/bash

rmmod uvcvideo
modprobe uvcvideo quirks=0x80
bash focusscript.sh
nice -n -19 bash /home/geneseas/robotics2425/startupcams.sh & python3 main.py 2> err.log && fg