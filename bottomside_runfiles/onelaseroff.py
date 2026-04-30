import gpiod
import sys

# Configuration
LASER_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"

def turn_off_laser():
    chip = None
    try:
        # Open the chip
        if hasattr(gpiod, "chip"):
            chip = gpiod.chip(GPIO_CHIP)
        else:
            chip = gpiod.Chip(GPIO_CHIP)

        line = chip.get_line(LASER_GPIO)

        # The error says it takes 2 to 3 arguments.
        # We will provide exactly 3: ("label", direction_int, value_int)
        # 3 = DIRECTION_OUTPUT
        # 0 = OFF
        line.request("laser_off", 3, 0)
        
        # Double-check the value is set to 0
        line.set_value(0)
        
        # Release the line
        line.release()
        print(f"Laser on GPIO {LASER_GPIO} is now OFF.")

    except PermissionError:
        print("Error: Permission denied. Please run with 'sudo'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if chip:
            # Clean up the chip reference
            del chip

if __name__ == "__main__":
    turn_off_laser()