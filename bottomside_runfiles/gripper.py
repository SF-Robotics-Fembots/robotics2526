import time, lgpio, gpiod
from gpiod.line import Direction, Value
import socket, json

#variables
#ip_address = "127.0.0.1" # 192.168.1.100
#ip_address = "192.168.1.100"
port = 40000
#gripper gpos
front_gripper = 17 #14
side_gripper = 27 #15

def main(ip_address):
    #client setup shenanigans
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port))
    print("client connected!")


    #gpo setup
    with gpiod.request_lines("/dev/gpiochip4", consumer="LED", config={
        front_gripper: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.INACTIVE
        )
    },) as request:
             with gpiod.request_lines("/dev/gpiochip4", consumer="LED", config={
                side_gripper: gpiod.LineSettings(
                direction=Direction.OUTPUT, output_value=Value.INACTIVE
            )
            },) as request2:
                while True: 
                    #print("client connected!")
                    data = client_socket.recv(1024)
                    data = data.decode()
                    print(data)
                    database = json.loads(data)

                    #write to the gripper
                    if(database["front"] == 1):
                        request.set_value(front_gripper, Value.ACTIVE)
                        print("open front")
                    elif(database["front"] == 0):
                        request.set_value(front_gripper, Value.INACTIVE)
                        print("close front")
                    if(database["back"] == 1):
                        request2.set_value(side_gripper, Value.ACTIVE)
                        print("open back")
                    elif(database["back"] == 0):
                        request2.set_value(side_gripper, Value.INACTIVE)
                        print("close back")

  

    

        


#always remember to call the function
if          __name__ == "__main__":
    main()