#!/usr/bin/env python3
"""
Thruster Characterization Program
Tests all 6 thrusters to find the minimum PWM values for forward and reverse movement.
Tests in 5 microsecond increments.
"""

import board
import busio
import adafruit_pca9685
import time
import csv
from datetime import datetime

def main():
    print("="*60)
    print("THRUSTER CHARACTERIZATION PROGRAM")
    print("="*60)
    print()
    
    # Initialize I2C and PCA9685
    i2c = busio.I2C(board.SCL, board.SDA)
    shield = adafruit_pca9685.PCA9685(i2c)
    
    # Setup external clock and frequency
    shield.mode1_reg = 0x10                    # SLEEP=1
    shield.mode1_reg = 0x10 | 0x40             # SLEEP=1 + EXTCLK=1
    shield.prescale_reg = 60                   # 25MHz / (4096 * 100Hz) - 1 = ~100Hz
    shield.mode1_reg = 0x40 | 0x20             # EXTCLK=1 + AI=1, wake up
    time.sleep(0.005)
    
    print("PCA9685 initialized with external 25MHz clock")
    print()
    
    # Define thruster channels
    thruster_channels = [
        ("Thruster 1", shield.channels[8]),   # J16
        ("Thruster 2", shield.channels[12]),  # J9
        ("Thruster 3", shield.channels[13]),  # J8
        ("Thruster 4", shield.channels[11]),  # J10
        ("Thruster 5", shield.channels[9]),   # J19
        ("Thruster 6", shield.channels[14]),  # J2
    ]
    
    # Initialize all thrusters to neutral (1500 microseconds)
    neutral_pw = 1500
    for name, channel in thruster_channels:
        set_throttle(channel, neutral_pw)
    
    # Data collection
    results = {
        "timestamp": datetime.now().isoformat(),
        "thrusters": {}
    }
    
    # Test each thruster
    for thruster_num, (thruster_name, channel) in enumerate(thruster_channels, 1):
        print(f"\n{'='*60}")
        print(f"Testing {thruster_name} (Channel {thruster_num}/{len(thruster_channels)})")
        print(f"{'='*60}")
        
        results["thrusters"][thruster_name] = {
            "forward": None,
            "reverse": None
        }
        
        # Test FORWARD direction (1500 → 2200 μs)
        print(f"\n[FORWARD TEST] Testing from 1500 to 2200 microseconds")
        print(f"Watch for movement. Press Enter when thruster starts moving, or 's' to skip.\n")
        
        forward_threshold = test_direction(
            channel, 
            thruster_channels, 
            start_pw=1500, 
            end_pw=2200, 
            increment=5,
            direction="FORWARD"
        )
        
        results["thrusters"][thruster_name]["forward"] = forward_threshold
        
        # Small pause between tests
        time.sleep(0.5)
        
        # Test REVERSE direction (1500 → 800 μs)
        print(f"\n[REVERSE TEST] Testing from 1500 to 800 microseconds")
        print(f"Watch for movement. Press Enter when thruster starts moving, or 's' to skip.\n")
        
        reverse_threshold = test_direction(
            channel,
            thruster_channels,
            start_pw=1500,
            end_pw=800,
            increment=-5,
            direction="REVERSE"
        )
        
        results["thrusters"][thruster_name]["reverse"] = reverse_threshold
        
        # Return all to neutral
        for _, ch in thruster_channels:
            set_throttle(ch, neutral_pw)
        time.sleep(0.3)
    
    # Return all thrusters to neutral
    for _, channel in thruster_channels:
        set_throttle(channel, neutral_pw)
    
    i2c.deinit()
    
    # Display and save results
    print(f"\n{'='*60}")
    print("CHARACTERIZATION COMPLETE - RESULTS")
    print(f"{'='*60}\n")
    
    print(f"{'Thruster':<15} {'Forward (μs)':<15} {'Reverse (μs)':<15}")
    print("-" * 45)
    
    for thruster_name in results["thrusters"]:
        forward = results["thrusters"][thruster_name]["forward"]
        reverse = results["thrusters"][thruster_name]["reverse"]
        
        forward_str = str(forward) if forward is not None else "N/A"
        reverse_str = str(reverse) if reverse is not None else "N/A"
        
        print(f"{thruster_name:<15} {forward_str:<15} {reverse_str:<15}")
    
    # Save to CSV
    filename = f"thruster_characterization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    save_results(filename, results)
    print(f"\nResults saved to: {filename}")

def set_throttle(channel, throttle_microseconds):
    """Convert microseconds (800-2200) to duty cycle and set channel"""
    # Convert microseconds to duty cycle (0-65535)
    # 1500 μs = 50% duty cycle = 32768
    # Formula: (throttle_microseconds / 20000) * 65536
    duty_cycle = int((throttle_microseconds / 20000) * 65536)
    channel.duty_cycle = duty_cycle

def test_direction(test_channel, all_channels, start_pw, end_pw, increment, direction):
    """
    Test a thruster in one direction, incrementing by 5 microseconds each step.
    Returns the threshold PWM where movement was detected, or None if skipped.
    """
    neutral_pw = 1500
    current_pw = start_pw
    
    while True:
        # Determine if we've reached the end
        if increment > 0 and current_pw > end_pw:
            break
        if increment < 0 and current_pw < end_pw:
            break
        
        # Set all other thrusters to neutral
        for name, channel in all_channels:
            if channel != test_channel:
                set_throttle(channel, neutral_pw)
        
        # Set test thruster to current PWM
        set_throttle(test_channel, current_pw)
        time.sleep(0.15)  # Wait for thruster to respond
        
        # Ask user for input
        prompt = f"  PWM: {current_pw:4d} μs (Duty: {int((current_pw/20000)*65536):5d}) - Thrusting? [y/n/s]: "
        user_input = input(prompt).lower().strip()
        
        if user_input == 'y':
            print(f"  ✓ Movement detected at {current_pw} μs")
            return current_pw
        elif user_input == 's':
            print(f"  ⊘ Test skipped for {direction}")
            return None
        
        # Continue incrementing
        current_pw += increment
    
    print(f"  ✗ No movement detected in {direction} range")
    return None

def save_results(filename, results):
    """Save characterization results to CSV file"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Timestamp', results['timestamp']])
        writer.writerow([])
        writer.writerow(['Thruster', 'Forward Threshold (μs)', 'Reverse Threshold (μs)'])
        
        # Data rows
        for thruster_name in sorted(results['thrusters'].keys()):
            forward = results['thrusters'][thruster_name]['forward']
            reverse = results['thrusters'][thruster_name]['reverse']
            
            writer.writerow([
                thruster_name,
                forward if forward is not None else 'N/A',
                reverse if reverse is not None else 'N/A'
            ])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
