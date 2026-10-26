import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
kit.servo[8].actuation_range = 180
kit.servo[8].set_pulse_width_range(500, 2500)
kit.servo[8].angle = 0
time.sleep(3)

try:
	while True:
		kit.servo[8].angle = 0
		time.sleep(1)
		kit.servo[8].angle = 90
		time.sleep(1)
		# kit.servo[8].angle = 270
		# time.sleep(1)
		kit.servo[8].angle = 180
		time.sleep(1)
		kit.servo[8].angle = 0

except KeyboardInterrupt:
    print("Keyboard interrupt")
