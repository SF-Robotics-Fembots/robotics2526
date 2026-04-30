import gpiod
import sys

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

        # 1. Create a config object if your version requires it
        # If gpiod.LineRequest exists, we use it to wrap the direction.
        if hasattr(gpiod, "LineRequest"):
            config = gpiod.LineRequest()
            config.consumer = "laser_off"
            config.request_type = 3  # 3 = DIRECTION_OUTPUT
            line.request(config)
        else:
            # 2. Final Fallback: Pure positional without keywords
            # Some versions expect: (consumer_string, request_type)
            # We try 0 as the value for OFF immediately during request if possible
            line.request("laser_off", 3, 0)

        # Ensure value is set to 0
        line.set_value(0)
        
        line.release()
        print(f"Laser on GPIO {LASER_GPIO} is now OFF.")

    except Exception as e:
        # If the above fails, let's try the absolute simplest call possible:
        try:
            line.request("laser_off", 3)
            line.set_value(0)
            line.release()
            print(f"Laser on GPIO {LASER_GPIO} is now OFF (via fallback).")
        except:
            print(f"An error occurred: {e}")
    finally:
        if chip:
            del chip

if __name__ == "__main__":
    turn_off_laser()