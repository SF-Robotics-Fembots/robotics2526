#library time!
import threading
import socket, hid, json
import time, pynput, keyboard
from pynput.keyboard import Key, Listener #pynput is a keyboard library that will read the key press
import pickle #idk what this does but it likes to dill the json!

#set the port to use in threading
port = 40000
#ip_address = "127.0.0.1" # 192.168.1.100
#ip_address = "192.168.1.100"
front = 1
back = 1
changed = 1

#list the input as a keyboard press
def on_release(key):
    global changed
    global front
    global back
     #the value as global so that we can use it outside of the function
    print("key pressed")
    if key == Key.tab:                  
        prev_front = front #set the previous front value to front; will be used to compare changes
        #prev_back = back

        #check if the front value changed
        if front == 1: front = 0
        else: front = 1

        #if back == back: back = back

        gripper_vals = {
            "front" : front,
            "back" : back
        }
        #get the message
        message = json.dumps(gripper_vals)
        message = message.encode()

        #check if changed
        if (prev_front != front):
            #client_connected.send(message) #sends through the socket connection
            print(message)
            client_connected.send(message)

    if key == Key.shift:
        #prev_front = front #set the previous front value to front; will be used to compare changes
        prev_back = back
        #prev_front = front

        #check if the back value changed
        if back == 1: back = 0
        else: back = 1

        gripper_vals = {
            "front" : front,
            "back" : back
        }
        #get the message
        message = json.dumps(gripper_vals)
        message = message.encode()

        #check if changed
        if (prev_back != back):
            #client_connected.send(message) #sends through the socket connection
            print(message)
            client_connected.send(message)


    #put a sleep in so the speed doesn't break the universe
    time.sleep(0.1)
        
#write the listener
def on_press(key):
    if key == Key.esc: return False


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
    #        on_press=on_press,
    with Listener(
        on_release=on_release) as listener:
        listener.join()

#run the function
if __name__ == "__main__":
    main()