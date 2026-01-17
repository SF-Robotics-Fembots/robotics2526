import threading
import socket, hid, json
import time, pynput, keyboard
from pynput.keyboard import Key, Listener 
#set the port to use in threading
port = 3030
#ip_address = "192.168.1.100"
laser = 0 #start off

def on_release(key):
    global changed
    global laser
    if key == Key.f1:
        print("laser press")
        prev_laser = laser #used to compare changes

        #check if the value changed
        if laser == 0: laser = 1
        else: laser = 0

        laser_vals = {
            "laser" : laser
        }

        message = json.dumps(laser_vals)
        message = message.encode()

        #check if changed
        if prev_laser!= laser:
            print(message)
            client_connected.send(message)


    #put a sleep in so the speed doesn't break the universe
    time.sleep(0.1)
        
#write the listener
def on_press(key):
    #use f1 to press key
    if key == Key.esc: 
        print("gripper press")
        return False


#main function
def main(ip_address):
    
    #begin the serversocket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_address, port))
    server_socket.listen(1)
    print("socket listening!")
    global client_connected

    #accept the client address
    (client_connected, client_address) = server_socket.accept()
   
    #start the listener
    with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
        listener.join()

#run the function
if __name__ == "__main__":
    main()