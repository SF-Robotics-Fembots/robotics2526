from smbus2 import SMBus
import time

PCA9685_ADDR = 0x40  # Default I2C address
MODE1_REG = 0x00
PRESCALE_REG = 0xFE

def read_byte(bus, addr, reg):
    return bus.read_byte_data(addr, reg)

def write_byte(bus, addr, reg, value):
    bus.write_byte_data(addr, reg, value)

def set_external_clock(bus):
    # Step 1: Read current MODE1 register
    mode1 = read_byte(bus, PCA9685_ADDR, MODE1_REG)
    print("read zero: " + str(mode1))

    # Step 2: Set mode 1 to 0
    mode1_sleep = mode1 | (1 << 4)
    write_byte(bus, PCA9685_ADDR, MODE1_REG, 0x00)
    time.sleep(0.01)
    print("read one: " + str(hex(read_byte(bus, PCA9685_ADDR, MODE1_REG))))

    # Step 3: Set sleep bit
    mode1_extclk = mode1_sleep | (1 << 7)
    write_byte(bus, PCA9685_ADDR, MODE1_REG, 0x10)
    time.sleep(0.01)
    print("read two: " + str(hex(read_byte(bus, PCA9685_ADDR, MODE1_REG))))

    write_byte(bus, PCA9685_ADDR, PRESCALE_REG, 0x3C4)
    print("read prescale: " + str(hex(read_byte(bus, PCA9685_ADDR, PRESCALE_REG))))

    # Step 4: set sleep and external oscillator
    mode1_awake = mode1_extclk & ~(1 << 4)
    write_byte(bus, PCA9685_ADDR, MODE1_REG, 0x50)
    time.sleep(0.001)  # Wait 500 µs or more
    print("read three: " + str(hex(read_byte(bus, PCA9685_ADDR, MODE1_REG))))

    write_byte(bus, PCA9685_ADDR, MODE1_REG, 0xD0)
    time.sleep(0.001)  # Wait 500 µs or more
    print("read four: " + str(hex(read_byte(bus, PCA9685_ADDR, MODE1_REG))))

def set_pwm_freq(bus, freq_hz, ext_clock_hz=25000000):
    # Calculate prescale for given clock and target frequency
    prescaleval = ext_clock_hz / (4096.0 * freq_hz) - 1
    prescale = int(round(prescaleval))

    # Go to sleep before writing prescale
    old_mode = read_byte(bus, PCA9685_ADDR, MODE1_REG)
    sleep_mode = (old_mode & 0x7F) | 0x10  # sleep
    write_byte(bus, PCA9685_ADDR, MODE1_REG, sleep_mode)

    write_byte(bus, PCA9685_ADDR, PRESCALE_REG, prescale)

    # Wake back up
    write_byte(bus, PCA9685_ADDR, MODE1_REG, old_mode)
    time.sleep(0.005)
    write_byte(bus, PCA9685_ADDR, MODE1_REG, old_mode | 0x80)  # Restart

# 🔧 Example Usage
with SMBus(1) as bus:  # Use I2C bus 1 on Raspberry Pi
    set_pwm_freq(bus, freq_hz=100)  # Set to 50 Hz for servos
    set_external_clock(bus)
   
