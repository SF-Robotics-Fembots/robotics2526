import pygame
import socket
import time, json

#global ip_server
def main(ip_server):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(ip_server)

    #assign a ratio value
    ratio = 0.6 #60% speed
        # do we still need this ratio value???
    
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    
    pygame.init()
    
    serverSocket.bind((ip_server, 9090)) #was 9090
    serverSocket.listen(1)
    print("socket listening joystick")
    
    (clientConnected, clientAddress) = serverSocket.accept()
    
    #the speed is initially set to fast
    # slow_speed = 0
    # prev_mode = slow_speed
    mode = 1
    prev_mode = mode

    while True:
        #print("joystick loop")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            #if event.type == pygame.JOYAXISMOTION:
            #    print(event)
            #if event.type == pygame.JOYBUTTONDOWN:
            #    print(event)

        if pygame.joystick.Joystick(0).get_button(1): mode = 0 #STOP - button 2
        # if pygame.joystick.Joystick(0).get_button(4): mode = 1 #FAST - button 5
        # if pygame.joystick.Joystick(0).get_button(2):mode = 0.5 #SLOW #PICKED_RANDOM_BUTTON_DECIDE_LATER - button 3
        elif pygame.joystick.Joystick(0).get_button(4): mode = 1 #FAST - button 5
        elif pygame.joystick.Joystick(0).get_button(2):mode = 0.5

        x_speed = (pygame.joystick.Joystick(0).get_axis(0))
        #if slow_speed: x_speed = x_speed*ratio
        x_speed *= mode
        y_speed = (pygame.joystick.Joystick(0).get_axis(1))
        #if slow_speed: y_speed = y_speed*ratio
        y_speed *= mode
        r_speed = (pygame.joystick.Joystick(0).get_axis(2))
        #if slow_speed: r_speed = r_speed*ratio
        r_speed *= mode
        v_speed = (pygame.joystick.Joystick(0).get_axis(3))
        v_speed *= mode
      
        if mode != prev_mode:
            if mode == 1:
                print ("FAST MODE")
            elif mode == 0.5:
                print ("SLOW MODE")
            elif mode == 0:
                print ("STOP MODE")
        prev_mode = mode

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
        time.sleep(.04) #.05
        
if __name__ == "__main__":
    main()