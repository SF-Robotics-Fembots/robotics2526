import gpiod
import lgpio
import socket
import json
import sys

PORT = 3030
GPIO_CHIP = "/dev/gpiochip4"
LASER_GPIO = 23
MESSAGE_KEYS = ("lasers",)


def _open_chip(path):
    if hasattr(gpiod, "chip"):
        return gpiod.chip(path)
    return gpiod.Chip(path)


def _lgpio_writer(path, line):
    chip_num = int(path.replace("/dev/gpiochip", ""))
    handle = lgpio.gpiochip_open(chip_num)
    lgpio.gpio_claim_output(handle, line)

    def _write(value):
        lgpio.gpio_write(handle, line, value)

    def _close():
        lgpio.gpiochip_close(handle)

    return _write, _close


def _gpiod_v2_writer():
    settings = gpiod.LineSettings(
        direction=gpiod.Direction.OUTPUT,
        output_value=gpiod.Value.INACTIVE,
    )
    request = gpiod.request_lines(GPIO_CHIP, consumer="LASER", config={
        LASER_GPIO: settings
    })

    def _write(value):
        desired = gpiod.Value.ACTIVE if value == 1 else gpiod.Value.INACTIVE
        request.set_value(LASER_GPIO, desired)

    def _close():
        request.close()

    return _write, _close


def _gpiod_v1_writer():
    chip = _open_chip(GPIO_CHIP)
    line = chip.get_line(LASER_GPIO)
    line.request(consumer="LASER", type=gpiod.LINE_REQ_DIR_OUT)
    line.set_value(0)

    def _write(value):
        line.set_value(value)

    def _close():
        line.release()
        chip.close()

    return _write, _close


def _make_writer():
    if (hasattr(gpiod, "request_lines")
            and hasattr(gpiod, "LineSettings")
            and hasattr(gpiod, "Direction")
            and hasattr(gpiod, "Value")):
        return _gpiod_v2_writer()
    if hasattr(gpiod, "LINE_REQ_DIR_OUT"):
        return _gpiod_v1_writer()
    return _lgpio_writer(GPIO_CHIP, LASER_GPIO)


def _extract_value(message):
    for key in MESSAGE_KEYS:
        if key in message:
            value = message[key]
            if value in (1, "1", True):
                return 1
            if value in (0, "0", False):
                return 0
    return None


def main(argv):
    if len(argv) != 2:
        print("Usage: python3 lasers.py <ip_address>")
        return 2

    ip_address = argv[1]
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, PORT))
    print("client connected!")

    write_value, close_writer = _make_writer()
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            text = data.decode()
            print(text)
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                continue

            if isinstance(payload, dict):
                desired = _extract_value(payload)
                if desired is not None:
                    write_value(desired)
    finally:
        close_writer()
        client_socket.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
