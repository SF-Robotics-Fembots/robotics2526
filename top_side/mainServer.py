#import main libraries
import pygame
import time
import socket
import threading

#import the threaded files
import joyServer
import piServer
import gripperServer
import pumpServer  

global ip_server
ip_server = "192.168.1.67" #192.168.1.100

joystickCode = threading.Thread(target=joyServer.main, args = (ip_server,))
inverseCode = threading.Thread(target=piServer.main, args = (ip_server,))
#gripperCode = threading.Thread(target=gripperServer.main, args=(ip_server,))
#pumpCode = threading.Thread(target=pumpServer.main, args=(ip_server,))



joystickCode.start()                                                                                                                            
inverseCode.start()
#gripperCode.start()
#pumpCode.start()



joystickCode.join()
inverseCode.join()
#gripperCode.join()
#pumpCode.join()