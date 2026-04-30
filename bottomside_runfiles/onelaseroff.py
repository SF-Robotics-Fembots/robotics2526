import gpiod
import sys

LASER_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"

def turn_off_laser():
    chip = None
    try:
        # 1. Open the chip
        if hasattr(gpiod, "chip"):
            chip = gpiod.chip(GPIO_CHIP)
        else:
            chip = gpiod.Chip(GPIO_CHIP)

        line = chip.get_line(LASER_GPIO)

        # 2. Determine the correct constant for Output
        # Some versions use gpiod.LINE_REQ_DIR_OUT
        # Others use gpiod.line.REQ_DIR_OUT
        if hasattr(gpiod, "LINE_REQ_DIR_OUT"):
            req_type = gpiod.LINE_REQ_DIR_OUT
        elif hasattr(gpiod.Line, "REQ_DIR_OUT"):
            req_type = gpiod.Line.REQ_DIR_OUT
        else:
            # Fallback to the raw integer value for 'output' in libgpiod v1
            req_type = 3 

        # 3. Request the line and set to 0
        line.request(consumer="laser_off", type=req_type)
        line.set_value(0)
        
        line.release()
        print(f"Laser on GPIO {LASER_GPIO} is now OFF.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if chip:
            del chip

if __name__ == "__main__":
    turn_off_laser()