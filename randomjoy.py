#libraries
import pygame
import time
import math

#initialize the joystick?
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

#initialize pygame
pygame.init()

#initializer variables
init_ratio = 0

def hatValue(ratio):
    past_ratio = ratio
    new_ratio = past_ratio
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break
        if event.type == pygame.JOYHATMOTION:
            #assign some values to the variables
            #x - left (-1) right (1)
            #y - up (1) down (-1)
            x, y = pygame.joystick.Joystick(0).get_hat(0)
            #either add or subtract x*0.1 to the ratio
            new_ratio = new_ratio + x*0.1

            #the ratio may not exceed 1 or be less than 0
            if new_ratio < 0:
                new_ratio = 0
            if new_ratio >= 1:
                new_ratio = 1

    #   if past_ratio != new_ratio:
        return new_ratio
  

            

def main():
    slow_speed = 0
    initratio = 0
    ratuo = 1

    while True:
        print("joystick loop")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
    
    # collect joystick values as -1 to 1

        if pygame.joystick.Joystick(0).get_button(5): slow_speed = 0
        if pygame.joystick.Joystick(0).get_button(3): slow_speed = 1
        
        print("slow_speed: " + str(slow_speed))

        x_speed = (pygame.joystick.Joystick(0).get_axis(0))

        ratuo = hatValue(initratio)
        print("ratuo: " + str(ratuo))
        if slow_speed: x_speed = x_speed*ratuo


        #put the thruster values in the dictionary
        thrusterMovements = {
            'x_speed' : x_speed
        }

        print(thrusterMovements)
        #reset the init_ratio
        initratio = ratuo

        
if __name__ == "__main__":
    main()

