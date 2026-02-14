#import main libraries
import pygame
import time
import socket
import threading

#import the threaded files
import joyServer
import piServer
#import gripperServer
import laserServer  

global ip_server
ip_server = "192.168.1.67" #192.168.1.100

joystickCode = threading.Thread(target=joyServer.main, args = (ip_server,))
inverseCode = threading.Thread(target=piServer.main, args = (ip_server,))
#gripperCode = threading.Thread(target=gripperServer.main, args=(ip_server,))
laserCode = threading.Thread(target=laserServer.main, args=(ip_server,))
#test


joystickCode.start()                                                                                                                            
inverseCode.start()
#gripperCode.start()
laserCode.start()


joystickCode.join()
inverseCode.join()
#gripperCode.join()
laserCode.join()