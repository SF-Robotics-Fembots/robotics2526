import pygame   #pip install pygame
import board	#pip install board
import busio	#pip install adafruit-blinka
import adafruit_pca9685 #pip install adafruit-circuitpython-pca9685
#from adafruit_servokit import ServoKit #pip install adafruit-circuitpython-servokit
import time
import socket, json, sys

def main(ip_server):
	# library setup
	pygame.init()

	#setting up the median of the 'off' values for the thrusters
	horiz_off_value = 1500
	horiz_thrust_offset = 0
	vert_off_value = 1500
	vert_thrust_offset = 0
	neutral_pwm = 1500
	#thruster_startup_pwm = [
	#	{"positive": 1510, "negative": 1460},  # T1
	#	{"positive": 1515, "negative": 1465},  # T2
	#	{"positive": 1555, "negative": 1440},  # T3
	#	{"positive": 1560, "negative": 1450},  # T4
	#	{"positive": 1515, "negative": 1465},  # T5
	#	{"positive": 1560, "negative": 1450},  # T6
	#]
	dynamic_change = 999

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

	# Manual external-clock + frequency setup (PCA9685 datasheet §7.3.5).
	# The library's shield.external_clock setter is a no-op on this install, so
	# we write the registers directly. EXTCLK can only be latched while SLEEP=1,
	# and can only be cleared by a power cycle / software reset.
	shield.mode1_reg = 0x10              # SLEEP=1
	shield.mode1_reg = 0x10 | 0x40       # SLEEP=1 + EXTCLK=1 (latches external 25MHz clock)
	shield.prescale_reg = 60             # 25e6 / (4096 * 100Hz) - 1 = 60  → ~100Hz PWM
	shield.mode1_reg = 0x40 | 0x20       # EXTCLK=1 + AI=1, wake up
	time.sleep(0.005)

	mode1 = shield.mode1_reg
	print(f"PCA9685 MODE1 = 0x{mode1:02X}  EXTCLK={'ON' if mode1 & 0x40 else 'OFF'}")

	thrusterChannel1 = shield.channels[8] #J16
	thrusterChannel2 = shield.channels[12] #J9
	thrusterChannel3 = shield.channels[13] #J8
	thrusterChannel4 = shield.channels[11] #J10
	thrusterChannel5 = shield.channels[9] #J19
	thrusterChannel6 = shield.channels[14] #J2
	thrusterChannel1.duty_cycle = 0x2666

	thrusters = [
		thrusterChannel1,
		thrusterChannel2,
		thrusterChannel3,
		thrusterChannel4,
		thrusterChannel5,
		thrusterChannel6
	]

	def set_throttle(channel, throttle_in, delay=0):
		throttlePW = int(throttle_in / 10000 * 65536)
		channel.duty_cycle = throttlePW
		time.sleep(0)

	def apply_startup_compensation(pwm, thresholds):
		if pwm == neutral_pwm:
			return neutral_pwm
		if pwm > neutral_pwm:
			return pwm + (thresholds["positive"] - neutral_pwm)
		return pwm - (neutral_pwm - thresholds["negative"])

	# def test_sequence(ip_server):
	# 	channels = [thrusterChannel1, thrusterChannel2, thrusterChannel3, thrusterChannel4, thrusterChannel5, thrusterChannel6]
	# 	throttle_sequence = [
	# 		2200,
	# 		1500,
	# 		2200,
	# 		1500,
	# 		2200,
	# 		1500,
	# 		2200,
	# 		1500,
	# 		2200,
	# 		1500,
	# 		2200,
	# 		1500,
	# 	]

	# 	for channel, throttle in zip(channels, throttle_sequence):
	# 		set_throttle(channel, throttle, delay=0)


	throttle_in = 2200
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel1.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 1500
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel1.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 2200
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel2.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 1500
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel2.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 2200
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel3.duty_cycle = throttlePW
	time.sleep(0 )

	throttle_in = 1500
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel3.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 2200
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel4.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 1500
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel4.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 2200
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel5.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 1500
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel5.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 2200
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel6.duty_cycle = throttlePW
	time.sleep(0)

	throttle_in = 1500
	throttlePW = int(throttle_in/10000*65536)
	thrusterChannel6.duty_cycle = throttlePW
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
			
	print("about to connect")

	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	clientSocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 192.169.1.100 is comp computer ip

	clientSocket.connect((ip_server, 9090))
	clientSocket1.connect((ip_server, 7070))
	print("connected")
	prevX = 0
	prevY = 0
	prevV = 0
	prevR = 0
	#everytime data is sent, previous values are set to 0 (updates & loops values)

	directionRecieved = "a" #not in pilot inversion
	direction = 1

	# main loop
	while True:
		try:
			dataFraud = (clientSocket.recv(1024)).decode()
			first_dict_end = dataFraud.find("}")
			dataFraud = dataFraud[0:(first_dict_end+1)]
			thrusterMovements = json.loads(dataFraud)
			#print(thrusterMovements)
			#time.sleep(1)
			if debug_l2: print("datafraud: " + dataFraud)
			#data = (clientSocket.recv(1024)).decode()
			if debug_l2: print("data " + data)

			print(f"Loop Start -------------------------------------------------")


			
			#x_speed = x_speed[1:]
			#[1:]: used for inverse orders/directions
			x_speed = thrusterMovements['x_speed']
			x_speed = float(x_speed)
	
			#y_speed = data[data.find('y'):data.find('r')]
			#y_speed = y_speed[1:]
			y_speed = thrusterMovements['y_speed']
			y_speed = float(y_speed)
			
			#r_speed = data[data.find('r'):data.find('v')]
			#r_speed = r_speed[1:]
			r_speed = thrusterMovements['r_speed']
			r_speed = float(r_speed)
			
			#v_speed = data[data.find('v'):data.find('x')]
			#v_speed = v_speed[1:]
			v_speed = thrusterMovements['v_speed']
			v_speed = float(v_speed)
			

			#lines 157-190: translates first measured joystick values, which comes as a float, from top side
			#then, the float goes through a char*
			#the float is translated through the char* (via parsing) into another float that the top computer can understand&receive

			diffX = x_speed - prevX
			diffY = y_speed - prevY
			diffR = r_speed - prevR
			diffV = v_speed - prevV
			#finding difference of speeds to evaluate which ones need power limiting 
			#values used in next if statement
			print(f"Time:{time.time()} | from topside - x_speed: {x_speed} | prevX: {prevX} |  y_speed: {y_speed} | prevY: {prevY}")

#MOD: diffValue = value_speed - prevValue

		# 	if (abs(diffX) > dynamic_change):
		# 		x_speed = prevX + ((diffX/abs(diffX)) * dynamic_change)
		# 	if (abs(diffY) > dynamic_change):
		# 		y_speed = prevY + ((diffY/abs(diffY)) * dynamic_change)
		# 	if (abs(diffR) > dynamic_change):
		# 		r_speed = prevR + ((diffR/abs(diffR)) * dynamic_change)
		# 	if (abs(diffV) > dynamic_change):
		# 		v_speed = prevV + ((diffV/abs(diffV)) * dynamic_change)
		# #helps manage power
		#if diffvalue is greater than .05, then it will assign speed a lower values by multiplying diffValue by .1
			print(f"Time:{time.time()} | after-adjusment x_speed:{x_speed} | y_speed:{y_speed} | r_speed:{r_speed} | v_speed:{v_speed}")

			prevX = x_speed
			prevY = y_speed
			prevR = r_speed
			prevV = v_speed

#MOD: prevValue = value_speed

			# multiplies original values by 100 (necessary for calculations)
			x_speed = int((x_speed)*50)
			y_speed = int((y_speed)*50)
			r_speed = int((r_speed)*25)
			v_speed = int((v_speed)*85)

			#print("R Speed: " + str(r_speed))
			#rotation compensation :(
			r_speed = int(r_speed + rot_comp * y_speed)
			r_speed = int(r_speed + slide_comp * x_speed)

			
			directionRecieved = ((clientSocket1.recv(1024)).decode())
			directionRecieved = directionRecieved[0]
			if (directionRecieved == "a"):
				direction = 1
			elif (directionRecieved == "b"):
				direction = -1
			else:
				direction = direction
			if debug_l2: print(directionRecieved)
			if debug_l2: print(direction)


			#xDirArray = [-1*direction, 1*direction, -1*direction, 1*direction]
			#yDirArray = [1*direction, 1*direction, -1*direction, -1*direction]
			#rDirArray = [-1, 1, 1, -1]
			#third thruster is now cw so the signs got flipped


            #REMEMBER TO TEST THESE NOW
			# FWD/BACK is "Y", SIDE TO SIDE is "X"
			# this is thruster 1 (front right), 2 (back right), 3 (front left), 4 (back left)
			# THIS IS FOR THRUSTER MOUNTING- CW/CCW is below (clock_array)
			
			yDirArray = [1*direction, -1*direction, 1*direction, -1*direction]
			xDirArray = [-1*direction, -1*direction, 1*direction, 1*direction]
			rDirArray = [-1, 1, 1, -1]
			vDirArray = [1, 1]

			# array for each horizontal thruster value
			oldThrusterVals = [0, 0, 0, 0]
			# array for each vertical thruster value
			oldVertThrusterVals = [0, 0]

			# loop to collect value for each thruster using horizontal calculation function
			for tNum in range(0,4):
				#goes through code four times
				oldThrusterVals[tNum] = int((calcHorizontal(x_speed, tNum, xDirArray) + calcHorizontal(y_speed, tNum, yDirArray) + calcHorizontal(r_speed, tNum, rDirArray)))
			# loop to collect value for each thruster using vertical calculation function
			for vNum in range(0,2):
				#goes through code two times
				oldVertThrusterVals[vNum] = int((calcVertical(v_speed, vNum, vDirArray)))

			clockArray = [1, 1, 1, 1]    #1 for CW, -1 for CCW
			clockVertArray = [-1, 1]

			thrusterVals = [0, 0, 0, 0]
			vertThrusterVals = [0, 0]

			for tNum in range(0, 4):
				thrusterVals[tNum] = int(oldThrusterVals[tNum] * clockArray[tNum])

			for vNum in range(0, 2):
				vertThrusterVals[vNum] = int(oldVertThrusterVals[vNum] * clockVertArray[vNum])

		# original print
			# adjusting range
			max_thruster = 0
			for thrusters in range(0,4):
				max_thruster = max(max_thruster, abs(thrusterVals[thrusters]))

			if (max_thruster != 0) and (max_thruster >= 50):
				for thrusters in range(0, 4):
					thrusterVals[thrusters] = int(thrusterVals[thrusters] * (50 / max_thruster))
					#lines 284-291: finds the maximum value of all throttle values, then limits them if needed


			# new lists for the adjusted values for our power functions
			powerThrusterVals = [0, 0, 0, 0]
			powerVertThrusterVals = [0, 0]

			# both for loops adjust the range of the thrusters to 1000-2000
			for thrusters in range(0, 4):
				if (thrusterVals[thrusters] == 0):
					powerThrusterVals[thrusters] = horiz_off_value
				else:
					#powerThrusterVals[thrusters] = 1489 + (((abs(thrusterVals[thrusters]))/thrusterVals[thrusters]) * (25 + (thrusterVals[thrusters] * 4.64)))
					powerThrusterVals[thrusters] = horiz_off_value + ((abs(thrusterVals[thrusters])/thrusterVals[thrusters]) * horiz_thrust_offset) + (thrusterVals[thrusters] * 7.0)
			#was 25 and 4.64
			#using 1489 because 1489 = median of thruster calibration (all thrusters stop at 1489)
			for vertThrusters in range(0, 2):
				if debug_l2: print(vertThrusterVals[vertThrusters])
				if (vertThrusterVals[vertThrusters] == 0):
					powerVertThrusterVals[vertThrusters] = vert_off_value
				else:
					#powerVertThrusterVals[vertThrusters] = 1489 + (((abs(vertThrusterVals[vertThrusters]))/vertThrusterVals[vertThrusters]) * (25 + (vertThrusterVals[vertThrusters] * 4.64)))
					powerVertThrusterVals[vertThrusters] = vert_off_value + ((abs(vertThrusterVals[vertThrusters])/vertThrusterVals[vertThrusters]) * vert_thrust_offset) + (vertThrusterVals[vertThrusters] * 7.0)
					#changed from *25 to *50 because verts on this year's robot have a 50 uS deadzone & horizontals only have 25 uS deadzone on each side of center
					#abs(vertThrusterVals[vertThrusters]) just tells direction



			# static power limiting
			finalHorDiff = abs(powerThrusterVals[1] - horiz_off_value)
			finalVertDiff = abs(powerVertThrusterVals[1] - vert_off_value)
			finalTotal = (finalHorDiff * 4) + (finalVertDiff * 2)
			if (finalTotal != 0):
				percent = (1700/finalTotal) #2400
				#finds percent to display how much we are exceeding power use (ex. exceeding power limit by 5%)
				if (finalTotal > 1700): #was 1950, max 2934
					for thruster in range(0, 4):
						Diff = powerThrusterVals[thruster] - horiz_off_value
						newDiff = Diff * (percent)
						powerThrusterVals[thruster] = horiz_off_value + newDiff
					for vertThruster in range(0, 2):
						vertDiff = powerVertThrusterVals[vertThruster] - vert_off_value
						newVertDiff = vertDiff * (percent)
						powerVertThrusterVals[vertThruster] = vert_off_value + newVertDiff
						#finding total thruster throttles and making sure power isnt exceeded
						#main power limiting
						#if power is exceeded, then values are made smaller in line 339

			#print("third print")
			#debug_l2 = 1
			
			#made changes starting here for duty cycle
			if debug_l2: print(powerThrusterVals)

			#Combine horizontal and vertical thruster values
			allPowerVals = powerThrusterVals + powerVertThrusterVals
			compensatedPowerVals = [
				apply_startup_compensation(val, thruster_startup_pwm[index])
				for index, val in enumerate(allPowerVals)
			]

			# Combine corresponding thruster objects
			allThrusters = [
				thrusterChannel1,
				thrusterChannel2,
				thrusterChannel3,
				thrusterChannel4,
				thrusterChannel5,
				thrusterChannel6
			]

			# Apply compensated PWM to each thruster and print values in a single row
			for thruster, val in zip(allThrusters, compensatedPowerVals):
				thruster.duty_cycle = int(val / 10000 * 65536)

			#print(*allPowerVals)

			# Print PWM values in a single row with labels
			labels = ["T1", "T2", "T3", "T4", "T5", "T6"]
			print(f"Time:{time.time()} | " + " | ".join(f"{label}:{val}" for label, val in zip(labels, compensatedPowerVals)))
			
			# Print actual ESC values (duty cycle)
			esc_vals = [int(val / 10000 * 65536) for val in compensatedPowerVals]
			print(f"ESC Values: " + " | ".join(f"{label}:{val}" for label, val in zip(labels, esc_vals)))


		except ValueError:
			print("Error")
			check = (clientSocket.recv(1024)).decode()
			print("check: " + check)
			print("dataFraud: " + dataFraud)
			print("dataFraud: " + dataFraud, file = sys.stderr)

if __name__ == "__main__":
    main()
