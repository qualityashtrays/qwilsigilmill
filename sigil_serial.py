import serial
import time

# Letter-to-number mapping
LETTER_MAP = {
    'A': 1, 'J': 1, 'S': 1,
    'B': 2, 'K': 2, 'T': 2,
    'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4,
    'E': 5, 'N': 5, 'W': 5,
    'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7,
    'H': 8, 'Q': 8, 'Z': 8,
    'I': 9, 'R': 9
}

# Magic square mapping
MAGIC_SQUARE = {
    1: (1, 1), 2: (2, 0), 3: (0, 1), 4: (0, 0), 
    5: (1, 1), 6: (2, 2), 7: (2, 1), 8: (0, 2), 
    9: (1, 0)
}

# Grid constants
GRID_SIZE = 100
CELL_SIZE = GRID_SIZE / 3
CENTER_OFFSET = CELL_SIZE / 2

def process_intent(intent):
    """ Remove vowels and duplicate letters, then convert to numbers """
    intent = intent.upper().replace(" ", "")
    vowels = "AEIOU"
    unique_letters = []

    for letter in intent:
        if letter not in vowels and letter not in unique_letters:
            unique_letters.append(letter)

    return [LETTER_MAP[letter] for letter in unique_letters if letter in LETTER_MAP]

def number_to_position(number):
    """Convert number to 3x3 grid position."""
    if number in MAGIC_SQUARE:
        col, row = MAGIC_SQUARE[number]
        x = col * CELL_SIZE + CENTER_OFFSET
        y = row * CELL_SIZE + CENTER_OFFSET
        return x, y
    return None

def add_circle_gcode(x, y, radius=3):
    """Approximate a small circle using short movements (GRBL-safe)"""
    circle_commands = [
        f"G0 X{x:.2f} Y{y:.2f} Z5",
        f"G1 X{x+radius:.2f} Y{y:.2f} F500",
        f"G1 X{x:.2f} Y{y+radius:.2f} F500",
        f"G1 X{x-radius:.2f} Y{y:.2f} F500",
        f"G1 X{x:.2f} Y{y-radius:.2f} F500",
        f"G1 X{x+radius:.2f} Y{y:.2f} F500"
    ]
    return circle_commands

def sigil_to_gcode(numbers):
    """Generate full G-code for GRBL"""
    gcode = ["G90 ; Absolute positioning", "G21 ; Use millimeters", "G0 Z5 ; Lift tool"]

    positions = [number_to_position(num) for num in numbers if number_to_position(num)]
    
    if positions:
        start_x, start_y = positions[0]
        gcode.extend(add_circle_gcode(start_x, start_y))
        gcode.append(f"G1 X{start_x:.2f} Y{start_y:.2f} F500")

        for x, y in positions:
            gcode.append(f"G1 X{x:.2f} Y{y:.2f} F500")

        end_x, end_y = positions[-1]
        gcode.append(f"G1 X{end_x+10:.2f} Y{end_y:.2f} F500")  # Exit line

    gcode.extend(["G0 Z5 ; Lift tool", "M5 ; Stop tool"])
    return "\n".join(gcode)

def send_gcode_to_serial(gcode, port="COM10", baudrate=115200):
    """Send generated G-code directly to GRBL via serial connection"""
    try:
        with serial.Serial(port, baudrate, timeout=2) as cnc:
            time.sleep(2)  # Wait for connection
            print("Connected to GRBL CNC on", port)

            # Unlock GRBL in case of alarm mode
            cnc.write("$X\r\n".encode())  
            time.sleep(0.5)

            print("Sending G-code...")
            for line in gcode.split("\n"):
                cnc.write((line + "\r\n").encode())  # Ensure GRBL parses commands properly
                time.sleep(0.1)  # Allow processing time

        print("G-code sent successfully!")

    except Exception as e:
        print(f"Error connecting to {port}: {e}")

# ** Run the full process **
intent = input("What is your intent? ")
sigil_numbers = process_intent(intent)
gcode_output = sigil_to_gcode(sigil_numbers)

print("\nGenerated G-code:\n", gcode_output)

# ** Send directly to serial connection ** 
send_gcode_to_serial(gcode_output, port="COM10", baudrate=115200)