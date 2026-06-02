#!/usr/bin/env python3
"""
Check if external crystal is being used on PCA9685
"""

import board  # pip install board
import busio  # pip install adafruit-blinka
import adafruit_pca9685  # pip install adafruit-circuitpython-pca9685

def check_external_clock():
    try:
        # Initialize I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Create PCA9685 shield object
        shield = adafruit_pca9685.PCA9685(i2c)
        
        # Read MODE1 register
        mode1_value = shield.mode1_reg
        
        # Check if EXTCLK bit is set (bit 6 = 0x40)
        extclk_enabled = bool(mode1_value & 0x40)
        
        # Display results
        print(f"PCA9685 MODE1 Register Value: 0x{mode1_value:02X} (binary: {bin(mode1_value)})")
        print(f"EXTCLK Bit (bit 6): {extclk_enabled}")
        print()
        
        if extclk_enabled:
            print("✓ EXTERNAL CRYSTAL IS BEING USED")
        else:
            print("✗ EXTERNAL CRYSTAL IS NOT BEING USED (internal oscillator active)")
        
        i2c.deinit()
        return extclk_enabled
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure:")
        print("  - PCA9685 is connected to I2C")
        print("  - Required libraries are installed:")
        print("    pip install board")
        print("    pip install adafruit-blinka")
        print("    pip install adafruit-circuitpython-pca9685")
        print("  - I2C is enabled on the system")
        return None

if __name__ == "__main__":
    check_external_clock()
