import gpiod
import sys

LASER_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"

def turn_off_laser():
    chip = None
    try:
        # Open chip - checking both common v1.x names
        if hasattr(gpiod, "chip"):
            chip = gpiod.chip(GPIO_CHIP)
        else:
            chip = gpiod.Chip(GPIO_CHIP)

        line = chip.get_line(LASER_GPIO)

        # In libgpiod v1.x:
        # 1 = Open drain
        # 2 = Open source
        # 3 = DIRECTION_OUTPUT (This is what we want)
        # We use the raw integer 3 to avoid 'AttributeError'
        line.request(consumer="laser_off", type=3)
        
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
            # Manually trigger cleanup since .close() is missing
            del chip

if __name__ == "__main__":
    turn_off_laser()