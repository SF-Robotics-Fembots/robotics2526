#!/bin/sh

#run the upgrade & download pip
apt-get update && apt-get install pip


#install the requirements.txt file
/home/geneseas/robotics2425/venv/bin/python3 -m /home/geneseas/robotics2425/venv/bin/python3-pip install -r requirements.txt
