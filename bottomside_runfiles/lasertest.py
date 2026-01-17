import gpiod
import sys

PUMP_GPIO = 23
GPIO_CHIP = "/dev/gpiochip4"


def main(argv):
    if len(argv) != 2 or argv[1] not in ("0", "1"):
        print("Usage: python3 lasertest.py 0|1")
        return 2

    desired_value = 1 if argv[1] == "1" else 0

    # Older gpiod API: open chip, request line, set value, then release.
    chip = gpiod.Chip(GPIO_CHIP)
    line = chip.get_line(PUMP_GPIO)
    line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
    line.set_value(desired_value)
    line.release()
    chip.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
