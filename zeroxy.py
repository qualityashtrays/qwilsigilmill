import serial
import time

def reset_axes(port="COM10", baudrate=115200):
    """Resets X and Y axes to zero by sending G92 X0 Y0"""
    try:
        with serial.Serial(port, baudrate, timeout=2) as cnc:
            time.sleep(2)  # Wait for connection
            print("Connected to GRBL on", port)

            # Send reset command
            cnc.write("G92 X0 Y0\r\n".encode())  
            time.sleep(0.5)  # Allow GRBL to process

            print("X and Y axes reset to 0!")

    except Exception as e:
        print(f"Error connecting to {port}: {e}")

# Run the function
reset_axes()