import gpiod
import sys

LASER_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"

def turn_off_laser():
    chip = None
    try:
        # Open chip
        if hasattr(gpiod, "chip"):
            chip = gpiod.chip(GPIO_CHIP)
        else:
            chip = gpiod.Chip(GPIO_CHIP)

        line = chip.get_line(LASER_GPIO)

        # In very old v1 wrappers, arguments are strictly positional:
        # Argument 1: Consumer String
        # Argument 2: Request Type (3 = Output)
        line.request("laser_off", 3)
        
        # Set value to 0 (OFF)
        line.set_value(0)
        
        line.release()
        print(f"Laser on GPIO {LASER_GPIO} is now OFF.")

    except PermissionError:
        print("Error: Permission denied. Please run with 'sudo'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if chip:
            del chip

if __name__ == "__main__":
    turn_off_laser()