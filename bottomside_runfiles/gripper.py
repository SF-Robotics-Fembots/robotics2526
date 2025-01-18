import time, lgpio
import socket, json

#variables
#ip_address = "127.0.0.1" # 192.168.1.100
port = 40000

def main(ip_address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port))
    print("client connected!")

    while True: 
        #print("client connected!")
        data = client_socket.recv(1024)
        data = data.decode()
        print(data)
        database = json.loads(data)
        print(str(database))


#always remember to call the function
main()