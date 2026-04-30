import gpiod
import sys

# Define the GPIO pin and chip
LASER_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"

def turn_off_laser():
    try:
        # Requesting the line as an output and setting it to INACTIVE (0)
        # Using a context manager ('with') ensures the pin is released properly
        with gpiod.request_lines(
            GPIO_CHIP,
            consumer="laser-control",
            config={LASER_GPIO: gpiod.LineSettings(
                direction=gpiod.Direction.OUTPUT,
                output_value=gpiod.Value.INACTIVE
            )}
        ) as request:
            print(f"Laser on GPIO {LASER_GPIO} has been turned OFF.")
            
    except FileNotFoundError:
        print(f"Error: GPIO chip {GPIO_CHIP} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    turn_off_laser()