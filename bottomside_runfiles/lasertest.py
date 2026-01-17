import gpiod
from gpiod.line import Direction, Value
import sys

PUMP_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"


def main(argv):
    if len(argv) != 2 or argv[1] not in ("0", "1"):
        print("Usage: python3 lasertest.py 0|1")
        return 2

    desired_value = Value.ACTIVE if argv[1] == "1" else Value.INACTIVE

    # GPIO setup and write once.
    with gpiod.request_lines(GPIO_CHIP, consumer="LED", config={
        PUMP_GPIO: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.INACTIVE
        )
    }) as request:
        request.set_value(PUMP_GPIO, desired_value)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
