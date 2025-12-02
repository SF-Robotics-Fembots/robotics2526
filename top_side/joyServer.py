import pygame
import socket
import time, json

#global ip_server



def main(ip_server):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(ip_server)

    #assign a ratio value
    ratio = 0.6 #60% speed
    
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    
    pygame.init()
    
    serverSocket.bind((ip_server, 9090)) #was 9090
    serverSocket.listen(1)
    print("socket listening joystick")
    
    (clientConnected, clientAddress) = serverSocket.accept()
    
    #the speed is initially set to fast
    slow_speed = 0

    while True:
        print("joystick loop")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            #if event.type == pygame.JOYAXISMOTION:
            #    print(event)
            #if event.type == pygame.JOYBUTTONDOWN:
            #    print(event)
            

        if pygame.joystick.Joystick(0).get_button(5): slow_speed = 0
        if pygame.joystick.Joystick(0).get_button(3): slow_speed = 1

        x_speed = (pygame.joystick.Joystick(0).get_axis(0))
        if slow_speed: x_speed = x_speed*ratio
        
        y_speed = (pygame.joystick.Joystick(0).get_axis(1))
        if slow_speed: y_speed = y_speed*ratio
       
        r_speed = (pygame.joystick.Joystick(0).get_axis(2))
        if slow_speed: r_speed = r_speed*ratio
       
        v_speed = (pygame.joystick.Joystick(0).get_axis(3))

        #put the thruster values in the dictionary
        thrusterMovements = {
            'x_speed' : x_speed,
            'y_speed' : y_speed,
            'r_speed' : r_speed,
            'v_speed' : v_speed
        }
        
        #send the json dict
        message = json.dumps(thrusterMovements)
        message = message.encode()
        clientConnected.send(message)

        #to slow down the loop because it goes faster than light
        time.sleep(.05)
        
if __name__ == "__main__":
    main()