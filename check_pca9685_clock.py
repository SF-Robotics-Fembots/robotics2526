#!/usr/bin/env python3
"""
Check if external crystal is being used on PCA9685
"""

import smbus2

# PCA9685 constants
PCA9685_ADDRESS = 0x40  # Default I2C address
MODE1_REG = 0x00        # MODE1 register address
EXTCLK_BIT = 6          # External clock enable bit (bit 6)

def check_external_clock():
    try:
        # Initialize I2C bus (usually bus 1 on Raspberry Pi)
        bus = smbus2.SMBus(1)
        
        # Read MODE1 register
        mode1_value = bus.read_byte_data(PCA9685_ADDRESS, MODE1_REG)
        
        # Check if EXTCLK bit is set (bit 6)
        extclk_enabled = (mode1_value >> EXTCLK_BIT) & 1
        
        bus.close()
        
        # Display results
        print(f"PCA9685 MODE1 Register Value: 0x{mode1_value:02X} (binary: {bin(mode1_value)})")
        print(f"EXTCLK Bit (bit 6): {extclk_enabled}")
        print()
        
        if extclk_enabled:
            print("✓ EXTERNAL CRYSTAL IS BEING USED")
        else:
            print("✗ EXTERNAL CRYSTAL IS NOT BEING USED (internal oscillator active)")
        
        return extclk_enabled
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure:")
        print("  - PCA9685 is connected to I2C bus 1")
        print("  - smbus2 is installed (pip install smbus2)")
        print("  - I2C is enabled on the system")
        return None

if __name__ == "__main__":
    check_external_clock()
