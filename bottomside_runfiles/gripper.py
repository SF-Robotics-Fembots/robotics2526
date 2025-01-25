import time, lgpio, gpiod
import socket, json

#variables
#ip_address = "127.0.0.1" # 192.168.1.100
ip_address = "192.168.1.100"
port = 40000
#gripper gpos
front_gripper = 20
side_gripper = 21

def main(ip_address):
    #gpo setup
    chip = gpiod.Chip('gpiochip4')
    line = chip.get_line(front_gripper) #uses lines to reference the gpios
    line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT) #sets to output

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port))
    print("client connected!")

    while True: 
        #print("client connected!")
        data = client_socket.recv(1024)
        data = data.decode()
        print(data)
        database = json.loads(data)

        #write to the gripper
        line.set_value(database["front"])

        


#always remember to call the function
main(ip_address)