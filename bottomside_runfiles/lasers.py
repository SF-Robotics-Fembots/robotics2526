import gpiod
import lgpio
import sys

LASER1_GPIO = 23
LASER2_GPIO = 24
GPIO_CHIP = "/dev/gpiochip4"


def _open_chip(path):
    if hasattr(gpiod, "chip"):
        return gpiod.chip(path)
    return gpiod.Chip(path)


def _request_output(line, value):
    if hasattr(gpiod, "LINE_REQ_DIR_OUT"):
        line.request(consumer="LASER", type=gpiod.LINE_REQ_DIR_OUT)
        line.set_value(value)
        return

    if hasattr(gpiod, "LineRequest"):
        request = gpiod.LineRequest()
        request.consumer = "LASER"
        if hasattr(gpiod.LineRequest, "DIRECTION_OUTPUT"):
            request.request_type = gpiod.LineRequest.DIRECTION_OUTPUT
        line.request(request, value)
        return

    raise RuntimeError("Unsupported gpiod API")


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

    # --- Modern gpiod v2 API ---
    if (hasattr(gpiod, "request_lines")
            and hasattr(gpiod, "LineSettings")
            and hasattr(gpiod, "Direction")
            and hasattr(gpiod, "Value")):

        settings = gpiod.LineSettings(
            direction=gpiod.Direction.OUTPUT,
            output_value=gpiod.Value.INACTIVE,
        )

        with gpiod.request_lines(GPIO_CHIP, consumer="LASERS", config={
            LASER1_GPIO: settings,
            LASER2_GPIO: settings
        }) as request:

            val = gpiod.Value.ACTIVE if desired_value else gpiod.Value.INACTIVE
            request.set_value(LASER1_GPIO, val)
            request.set_value(LASER2_GPIO, val)

        return 0

    # --- Older gpiod fallback ---
    try:
        chip = _open_chip(GPIO_CHIP)

        line1 = chip.get_line(LASER1_GPIO)
        line2 = chip.get_line(LASER2_GPIO)

        _request_output(line1, desired_value)
        _request_output(line2, desired_value)

        line1.release()
        line2.release()
        chip.close()

    except RuntimeError:
        _lgpio_write(GPIO_CHIP, LASER1_GPIO, desired_value)
        _lgpio_write(GPIO_CHIP, LASER2_GPIO, desired_value)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))