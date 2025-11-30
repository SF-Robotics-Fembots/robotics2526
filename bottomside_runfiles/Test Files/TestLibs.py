import gpiod
print("VENV gpiod:",getattr(gpiod, "__version__", "NO VERSION"), gpiod.__file__)

import lgpio
print("lgio from:", lgpio.__file__)
print("has gpiochip_open:", hasattr(lgpio,"gpiochip_open"))

import board, digitalio
print("Board OK", board)