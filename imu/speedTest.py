#tests speed

import time
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250

mpu = MPU9250(
	address_ak=AK8963_ADDRESS,
	address_mpu_master=MPU9050_ADDRESS_68,
	address_mpu_slave = MPU9050_ADDRESS_68,
	bus=1,
	gfs=GFS_1000,
	afs=AFS_8G,
	mfs=AK8963_BIT_16,
	mode = AK8963_MODE_C100HZ)

#mpu.calibrate()
acceleration_x = [0]*2
time.sleep(1)
total = 0
new_valx = 0
speed = 0
timet = [0]*2
mpu.configure()

#gets average
for i in range (100):
	total += mpu.readAccelerometerMaster()[0]
total = total/100
print("total: ", total)

while True:
	new_valx = mpu.readAccelerometerMaster()[0] - total
	clock = time.time()
#	print("Time: ", clock)
#	print("Acceleration: ", new_valx)
	acceleration_x[1] =  acceleration_x[0]
	timet[1] = timet[0]
	acceleration_x[0] = new_valx
	timet[0] = clock
	diff = timet[0]-timet[1]
	print(acceleration_x)
	print(diff)
	speed=round(speed+((acceleration_x[0]+acceleration_x[1])/2)*(diff), 5)
	print("speed: ", speed)
	time.sleep(2)
