import gpiod

# Settings
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

        # We avoid passing a string entirely to stop the 'str' attribute error.
        # We pass only the direction type as a keyword argument.
        # 3 is the standard integer for DIRECTION_OUTPUT in v1.x
        line.request(type=3)
        
        # Set to 0 (OFF)
        line.set_value(0)
        
        # Release and print
        line.release()
        print(f"Laser on GPIO {LASER_GPIO} is now OFF.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if chip:
            del chip

if __name__ == "__main__":
    turn_off_laser()