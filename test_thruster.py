import time
import board
import busio
import adafruit_pca9685

# ========================
# Configuration
# ========================
PWM_FREQUENCY = 97          # Hz (Blue Robotics ESC standard)
NEUTRAL_US = 1500           # Stop signal
ARM_HIGH_US = 2200          # Optional arming pulse
ARM_LOW_US = 1500           # Neutral after arming

# Thruster channels on PCA9685
THRUSTER_CHANNELS = [8, 10, 15, 13, 9, 14]  # 6 thrusters

def us_to_duty_cycle(pulse_us):
    """
    Convert microseconds to 16-bit duty cycle
    """
    return int((pulse_us / 10000) * 65535)

# Main Initialization
def initialize_thrusters():
    print("Initializing I2C...")
    i2c = busio.I2C(board.SCL, board.SDA)

    print("Initializing PCA9685...")
    pca = adafruit_pca9685.PCA9685(i2c)
    pca.frequency = PWM_FREQUENCY

    thrusters = [pca.channels[ch] for ch in THRUSTER_CHANNELS]

    print("Arming thrusters...")

    # Optional arming pulse (some ESCs require this)
    for t in thrusters:
        t.duty_cycle = us_to_duty_cycle(ARM_HIGH_US)
    time.sleep(0.5)

    # Set all thrusters to neutral (STOP)
    for t in thrusters:
        t.duty_cycle = us_to_duty_cycle(ARM_LOW_US)
    time.sleep(1.5)

    print("Thrusters initialized and idle at neutral (1500 µs).")

# ========================
# Entry Point
# ========================
if __name__ == "__main__":
    try:
        initialize_thrusters()
        while True:
            time.sleep(1)  # Keep program alive
    except KeyboardInterrupt:
        print("\nShutting down thrusters...")
