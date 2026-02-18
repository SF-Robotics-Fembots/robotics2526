import pygame   #pip install pygame
import board	#pip install board
import busio	#pip install adafruit-blinka
import adafruit_pca9685 #pip install adafruit-circuitpython-pca9685
from adafruit_servokit import ServoKit #pip install adafruit-circuitpython-servokit
import time
import socket, json, sys

def main():
	# library setup
	pygame.init()

	wait_time = 0.5
	go_fwd = 1800

#checking
# 	

	#setting up the median of the 'off' values for the thrusters
	horiz_off_value = 1500
	horiz_thrust_offset = 0
	vert_off_value = 1500
	vert_thrust_offset = 0

	#MODE1_REG = 0x00

	#debug! make more laters
	debug_l2 = 0

	#rotation compensation
	rot_comp = 0#was -0.08
	slide_comp =0 #0.19

	i2c = busio.I2C(board.SCL, board.SDA)
	#i2c.write_byte_data(0x40, 0x00, 0x10)
	#time.sleep(0.01)
	#i2c.write_byte_data(0x40, 0x00, 0x50)
	#time.sleep(0.01)
	shield = adafruit_pca9685.PCA9685(i2c)
	shield.external_clock = True #enable 25MHz external crystal
	kit = ServoKit(channels=16)
	shield.frequency = 96

	thrusterChannels = [
		shield.channels[8],  # Thruster 1
		shield.channels[12], # Thruster 2
		shield.channels[13], # Thruster 3
		shield.channels[11], # Thruster 4
		shield.channels[9],  # Thruster 5
		shield.channels[14], # Thruster 6
	]
	thrusterChannels[0].duty_cycle = 0x2666

	def set_throttle(channel, throttle_in, delay=0):
		throttlePW = int(throttle_in / 10000 * 65536)
		channel.duty_cycle = throttlePW
		time.sleep(delay)


	for channel in thrusterChannels:
		throttlePW = int(2200/10000*65536)
		channel.duty_cycle = throttlePW
		time.sleep(0)
		throttlePW = int(1500/10000*65536)
		channel.duty_cycle = throttlePW
		time.sleep(0)
	
	#horizontal thrusters calculations
	def calcHorizontal(joyValue, thrusterNum, direction):
		if (-5 <= joyValue <= 5):         # can adjust to create deadzone
			return 0
		else:
			joyValue = joyValue - ((abs(joyValue)/joyValue) * 5)
			return joyValue * direction[thrusterNum]


	# vertical thrusters calculations
	def calcVertical(joyValue, thrusterNum, direction):
		if (-15 <= joyValue <= 15):
			return 0
		else:
			joyValue = joyValue - ((abs(joyValue)/joyValue) * 10) # was 5
			return joyValue * direction[thrusterNum]
			
	while True:
		# main loop
		for i, channel in enumerate(thrusterChannels):
			print(f"Testing Thruster {i + 1}")
			input("Press Enter to continue...")
			throttlePW = int(go_fwd/10000*65536)
			channel.duty_cycle = throttlePW
			time.sleep(wait_time)
			throttlePW = int(1500/10000*65536)
			channel.duty_cycle = throttlePW
			time.sleep(wait_time)

if __name__ == "__main__":
	main()