#!/usr/bin/bash

#making a new bash script to run the camera GPIOs

/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio 0x0424 0x2732 0x01 2 0
/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio 0x0424 0x2732 0x01 3 1
/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio 0x0424 0x2732 0x01 7 0
/home/geneseas/robotics2526/Linux_USB57xx_58xx_59xx_ACE_V1.0/examples/gpio/out/gpio 0x0424 0x2732 0x01 9 1

