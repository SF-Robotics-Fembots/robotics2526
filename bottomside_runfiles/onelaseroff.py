import gpiod
import sys

LASER_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"

def turn_off_laser():
    chip = None
    try:
        # Check for lowercase 'chip' first (common in v1.x)
        if hasattr(gpiod, "chip"):
            chip = gpiod.chip(GPIO_CHIP)
        else:
            chip = gpiod.Chip(GPIO_CHIP)

        # Get the line
        line = chip.get_line(LASER_GPIO)

        # Request as output and set to 0 (OFF)
        # Using LINE_REQ_DIR_OUT constant
        line.request(consumer="laser_off", type=gpiod.LINE_REQ_DIR_OUT)
        line.set_value(0)
        
        # Release the line so other programs can use it later
        line.release()
        
        print(f"Laser on GPIO {LASER_GPIO} is now OFF.")

    except PermissionError:
        print("Error: Access denied. Please run with 'sudo'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # In v1.x, we just delete the reference to trigger cleanup
        if chip:
            del chip

if __name__ == "__main__":
    turn_off_laser()