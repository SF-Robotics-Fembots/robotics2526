import lgpio
print("lgio from:", lgpio.__file__)
print("has gpiochip_open:", hasattr(lgpio,"gpiochip_open"))

import board, digitalio
print("Board OK", board)