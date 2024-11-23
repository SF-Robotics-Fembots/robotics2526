#import main libraries
import pygame
import time
import socket
import threading

#import the threaded files
import joyServer
import pilotInverseServer

global ip_server
ip_server = "192.168.1.100"

joystickCode = threading.Thread(target=joyServer.main, args = (ip_server,))
inverseCode = threading.Thread(target=pilotInverseServer.main, args = (ip_server,))



joystickCode.start()
inverseCode.start()

joystickCode.join()
inverseCode.join()
