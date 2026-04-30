import gpiod
import sys

LASER_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"

def turn_off_laser():
    chip = None
    try:
        # Detect if it's .chip() or .Chip() in your version
        if hasattr(gpiod, "chip"):
            chip = gpiod.chip(GPIO_CHIP)
        elif hasattr(gpiod, "Chip"):
            chip = gpiod.Chip(GPIO_CHIP)
        else:
            print("Error: Could not find chip/Chip attribute in gpiod module.")
            return

        # Get the line
        line = chip.get_line(LASER_GPIO)

        # Request as output and set to 0
        line.request(consumer="laser_off", type=gpiod.LINE_REQ_DIR_OUT)
        line.set_value(0)
        
        # Clean up
        line.release()
        print(f"Laser on GPIO {LASER_GPIO} is now OFF.")

    except PermissionError:
        print("Error: Access denied. Please run with 'sudo'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if chip:
            chip.close()

if __name__ == "__main__":
    turn_off_laser()