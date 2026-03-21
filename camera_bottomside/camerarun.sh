<<<<<<< HEAD
#ustreamer --device=/dev/video$1 --host=192.168.1.68 --format=MJPEG --port=808$1 --device-timeout 2 -r 800x600 -b 2 --workers 2 --encoder=HW -n

#!/bin/bash

#!/bin/bash

DEVICE=${1:-0}
PORT=$((8080 + DEVICE))

ustreamer \
  --device=/dev/video$DEVICE \
  --host=192.168.1.68 \
  --format=MJPEG \
  --port=$PORT \
  --device-timeout 2 \
  -r 800x600 \
  -b 2 \
  --workers 2 \
  --encoder=HW \
  -n
=======
ustreamer --device=/dev/video$1 --host=192.168.1.68 --format=MJPEG --port=808$1 --device-timeout 2 -r 800x600 -b 2 --workers 2 --encoder=HW
>>>>>>> cd47fe3e29a1e9faf496316214b3223db8e47bd8
