from adafruit_servokit import ServoKit
import busio
from board import SCL, SDA

# Explicit I2C bus initialization
i2c = busio.I2C(SCL, SDA)

# Initialize the PCA9685 with 16 channels using the I2C bus
kit = ServoKit(channels=16, i2c=i2c)

# Servo configuration
kit.servo[0].actuation_range = 270  # body rotation
kit.servo[0].set_pulse_width_range(500, 2500)

kit.servo[2].actuation_range = 270  # head nod
kit.servo[2].set_pulse_width_range(500, 2500)

kit.servo[4].actuation_range = 270  # head rotation
kit.servo[4].set_pulse_width_range(500, 2500)

kit.servo[8].actuation_range = 180  # left arm
kit.servo[8].set_pulse_width_range(500, 2500)

kit.servo[10].actuation_range = 180  # right arm
kit.servo[10].set_pulse_width_range(500, 2500)

try:
    kit.servo[0].angle = 125    # body yaw
    kit.servo[2].angle = 40      # Head pitch (75 when tensioning belt)
    kit.servo[4].angle = 120    # head yaw
    kit.servo[8].angle = 135    # Left arm (135 when mounting)
    kit.servo[10].angle = 45    # Right arm (45 when mounting)
except KeyboardInterrupt:
    print("Keyboard interrupt")
