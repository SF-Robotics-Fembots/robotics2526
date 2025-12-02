ustreamer --device=/dev/video$1 --host=192.168.1.99 --format=MJPEG --port=808$1 --device-timeout 2 -r 800x600 -b 2 --workers 2 --encoder=HW
