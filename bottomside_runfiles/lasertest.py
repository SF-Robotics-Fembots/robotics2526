import gpiod
import lgpio
import sys

PUMP_GPIO = 10
GPIO_CHIP = "/dev/gpiochip4"


def _open_chip(path):
    if hasattr(gpiod, "chip"):
        return gpiod.chip(path)
    return gpiod.Chip(path)


def _request_output(line, value):
    # libgpiod v1 API
    if hasattr(gpiod, "LINE_REQ_DIR_OUT"):
        line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
        line.set_value(value)
        return

    # libgpiod v2 C++ bindings API
    if hasattr(gpiod, "LineRequest"):
        request = gpiod.LineRequest()
        request.consumer = "LED"
        if hasattr(gpiod.LineRequest, "DIRECTION_OUTPUT"):
            request.request_type = gpiod.LineRequest.DIRECTION_OUTPUT
        line.request(request, value)
        return

    raise RuntimeError("Unsupported gpiod API; cannot request output line.")


def _lgpio_write(path, line, value):
    chip_num = int(path.replace("/dev/gpiochip", ""))
    handle = lgpio.gpiochip_open(chip_num)
    lgpio.gpio_claim_output(handle, line)
    lgpio.gpio_write(handle, line, value)
    lgpio.gpiochip_close(handle)


def main(argv):
    if len(argv) != 2 or argv[1] not in ("0", "1"):
        print("Usage: python3 lasertest.py 0|1")
        return 2

    desired_value = 1 if argv[1] == "1" else 0

    # Preferred API in libgpiod v2 python bindings.
    if (hasattr(gpiod, "request_lines")
            and hasattr(gpiod, "LineSettings")
            and hasattr(gpiod, "Direction")
            and hasattr(gpiod, "Value")):
        settings = gpiod.LineSettings(
            direction=gpiod.Direction.OUTPUT,
            output_value=gpiod.Value.INACTIVE,
        )
        with gpiod.request_lines(GPIO_CHIP, consumer="LED", config={
            PUMP_GPIO: settings
        }) as request:
            desired = gpiod.Value.ACTIVE if desired_value == 1 else gpiod.Value.INACTIVE
            request.set_value(PUMP_GPIO, desired)
        return 0

    try:
        chip = _open_chip(GPIO_CHIP)
        line = chip.get_line(PUMP_GPIO)
        _request_output(line, desired_value)
        line.release()
        chip.close()
    except RuntimeError:
        _lgpio_write(GPIO_CHIP, PUMP_GPIO, desired_value)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
