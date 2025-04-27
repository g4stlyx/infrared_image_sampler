import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import os

def main():
    print("Use S to sample, Q to quit")
    
    file_prefix = input("File Name:\n")
    
    # Create output directory structure
    out_dir = "out"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
        print(f"Created directory: {out_dir}")
    
    sample_dir = os.path.join(out_dir, file_prefix)
    if not os.path.exists(sample_dir):
        os.mkdir(sample_dir)
        print(f"Created directory: {sample_dir}")
    
    # Ask user for temperature scaling factor (no need)
    scale_factor = 10.0  # Default scaling factor
    # user_scale = input("Enter temperature scaling factor (default is 10): ")
    # if user_scale.strip():
    #     try:
    #         scale_factor = float(user_scale)
    #         print(f"Using scale factor: {scale_factor}")
    #     except ValueError:
    #         print(f"Invalid input, using default scale factor: {scale_factor}")
    
    # Setup serial connection with shorter timeout for faster reading
    ser = serial.Serial('COM3', 115200, timeout=0.1)  # Reduced timeout, from 1 or 0.5
    time.sleep(2)  # Allow time for connection to establish
    
    sample = 0
    raw_temp = np.zeros((24, 32), dtype=int)  # Temporary array for raw values
    temperature = np.zeros((24, 32), dtype=int)  # Integer array for normalized values
    finish = False
    
    while not finish:
        # Reduced delay between loop iterations
        time.sleep(0.05)  # Reduced from 0.1
        char_input = 'S'
        
        if char_input == 'S':
            ser.write(b'S')
            stop_stream = False
            
            # Clear any pending data
            ser.reset_input_buffer()
            
            # Reset row and col at the beginning of each capture
            row = 0
            col = 0
            
            print("Waiting for data stream...")
            
            # Add timeout mechanism for data reading
            start_time = time.time()
            timeout_duration = 5  # 5 seconds timeout
            
            while not stop_stream and (time.time() - start_time < timeout_duration):
                if ser.in_waiting > 0:
                    rv = ser.readline().decode('ascii', errors='replace').strip()
                    read_value = 'X' if not rv else rv
                    # Reduce debug output frequency to improve performance
                    if read_value in ['Start', 'End', 'NewLine']:
                        print(f"Received: '{read_value}'")
                    
                    if read_value == 'X':
                        stop_stream = False
                    elif read_value == 'Start':
                        row = 0
                        col = 0
                        print("Starting capture frame")
                    elif read_value == 'NewLine':
                        row += 1
                        col = 0
                        if row % 5 == 0:  # Print only every 5th row to reduce console output
                            print(f"New row: {row}")
                        if row >= 24:
                            print(f"Warning: Row index {row} exceeds array dimensions (24). Capping at 23.")
                            row = 23
                    elif read_value == 'End':
                        stop_stream = True
                        print("Finished capture frame")
                    else:
                        try:
                            # Store the raw integer value
                            raw_value = int(float(read_value))
                            
                            # Add bounds checking before assignment
                            if 0 <= row < 24 and 0 <= col < 32:
                                raw_temp[row, col] = raw_value
                                col += 1
                            else:
                                print(f"Warning: Index out of bounds - row: {row}, col: {col}")
                        except ValueError:
                            print(f"Warning: Could not convert value '{read_value}' to integer")
                else:
                    # Even shorter delay when waiting for data to be available
                    time.sleep(0.005)  # Reduced from 0.01
            
            if time.time() - start_time >= timeout_duration:
                print("Timeout reached while waiting for data. Aborting capture.")
                continue
            
            # Calculate normalized temperature by dividing by scale factor and rounding
            temperature = np.round(raw_temp / scale_factor).astype(int)
            
            # Save only the normalized data with new directory structure
            filename = os.path.join(sample_dir, f"{file_prefix}_{sample}.txt")
            
            print(f"Saving normalized data file: {filename}")
            with open(filename, 'w') as file:
                for i in range(24):
                    for j in range(32):
                        file.write(f"{temperature[i, j]} ")
                    file.write("\n")
            
            # Print statistics for debugging
            print(f"Real temperature - min: {np.min(temperature)}, max: {np.max(temperature)}, mean: {np.mean(temperature):.1f}°C")
            
            # Visualization with only normalized data
            plt.figure(1, figsize=(10, 8))
            
            # Auto-range visualization
            plt.subplot(1, 2, 1)
            plt.imshow(temperature, cmap='jet')
            plt.colorbar(label='Temperature (°C)')
            plt.title(f"Temperature (Auto Range) - Sample {sample}")
            
            # Fixed range visualization - adjusted for human body temperature range
            plt.subplot(1, 2, 2)
            temp_min = 20  # Room temperature-ish
            temp_max = 40  # Higher maximum to properly capture human body temperature
            plt.imshow(temperature, vmin=temp_min, vmax=temp_max, cmap='jet')
            plt.colorbar(label='Temperature (°C)')
            plt.title(f"Temperature (Fixed Range: {temp_min}-{temp_max}°C)")
            
            plt.tight_layout()
            plt.pause(0.5)
            
        if char_input == 'Q':
            finish = True
            
        sample += 1
        # Reduced delay between samples
        time.sleep(0.5)  # Reduced from 1
    
    ser.close()
    print("Connection closed")

if __name__ == "__main__":
    main()