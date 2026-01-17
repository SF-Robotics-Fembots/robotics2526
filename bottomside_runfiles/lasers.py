import time, lgpio, gpiod
from gpiod.line import Direction, Value
import socket, json

#variables
#ip_address = "192.168.1.100"
port = 3030
#pump gpio
pump = 23


def main(ip_address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port))
    print("client connected!")


    #gpo setup
    with gpiod.request_lines("/dev/gpiochip4", consumer="LED", config={
        pump: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.INACTIVE
        )
    },) as request:
            while True: 
                #print("client connected")
                data = client_socket.recv(1024)
                data = data.decode()
                print(data)
                database = json.loads(data)

                #write to pump
                if(database["pump"] == 1):
                     request.set_value(pump, Value.ACTIVE)
                elif(database["pump"] == 0):
                     request.set_value(pump, Value.INACTIVE)

if  __name__ == "__main__":
    main()