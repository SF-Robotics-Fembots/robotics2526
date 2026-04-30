import gpiod

# Constants
LASER_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"

def turn_off_laser():
    # 1. Open the GPIO chip
    # v1.x uses gpiod.Chip() or gpiod.chip()
    try:
        chip = gpiod.Chip(GPIO_CHIP)
    except Exception as e:
        print(f"Could not open chip {GPIO_CHIP}: {e}")
        return

    try:
        # 2. Get the specific line for the laser
        line = chip.get_line(LASER_GPIO)

        # 3. Request the line as an output
        # LINE_REQ_DIR_OUT is the v1.x constant for output mode
        line.request(consumer="laser_off_script", type=gpiod.LINE_REQ_DIR_OUT)

        # 4. Set value to 0 (Off)
        line.set_value(0)
        
        print(f"Success: Laser on GPIO {LASER_GPIO} is now OFF.")

        # 5. Clean up
        line.release()
    finally:
        chip.close()

if __name__ == "__main__":
    turn_off_laser()