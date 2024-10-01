import smbus2
import time
import RPi.GPIO as GPIO
import threading

# Initialize I2C bus
bus = smbus2.SMBus(1)  # For Raspberry Pi, use I2C bus 1

# GPIO Pins for Buttons
BUTTON_PIN = 10  # You can modify this to add more buttons
BUTTON_PIN1 = 23  # You can modify this to add more buttons

counter = 0
button_press_count = 0
button_press_count1 = 0
button_held = False  # State to track if the button is held
lock = threading.Lock()  # To prevent race conditions

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# LCD I2C address (detected via i2cdetect command)
I2C_ADDR = 0x3f  # Replace with your actual I2C address

# LCD Constants
LCD_WIDTH = 16  # Maximum characters per row for a 16x2 LCD
LCD_CHR = 1     # Sending data
LCD_CMD = 0     # Sending commands

# LCD RAM addresses for lines
LINE_1 = 0x80  # Address for first line
LINE_2 = 0xC0  # Address for second line

# Backlight control
LCD_BACKLIGHT = 0x08  # On
LCD_NOBACKLIGHT = 0x00  # Off

# Control flags
LCD_BACKLIGHT = 0x08  # Backlight ON
ENABLE = 0b00000100   # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Low-level function to send data
def lcd_byte(bits, mode):
    """ Send byte to data pins via I2C """
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # Send high bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Send low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    """ Toggle enable """
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)

def lcd_init():
    """ Initialize display """
    lcd_byte(0x33, LCD_CMD)  # Initialize
    lcd_byte(0x32, LCD_CMD)  # Set to 4-bit mode
    lcd_byte(0x06, LCD_CMD)  # Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # Turn on display, no cursor
    lcd_byte(0x28, LCD_CMD)  # 2 line display, 5x8 matrix
    lcd_byte(0x01, LCD_CMD)  # Clear display
    time.sleep(E_DELAY)

def lcd_clear():
    """ Clear the display """
    lcd_byte(0x01, LCD_CMD)  # Clear display
    time.sleep(E_DELAY)

def lcd_message(message):
    """ Send string to display """
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def lcd_set_cursor(line, col):
    """ Move cursor to specified row and column """
    if line == 0:
        address = LINE_1 + col
    elif line == 1:
        address = LINE_2 + col
    else:
        raise ValueError("Invalid line. Use 0 for line 1, 1 for line 2.")

    lcd_byte(address, LCD_CMD)

# Function to turn off backlight
def lcd_backlight_off():
    bus.write_byte(I2C_ADDR, LCD_NOBACKLIGHT)

# Function to turn on backlight
def lcd_backlight_on():
    bus.write_byte(I2C_ADDR, LCD_BACKLIGHT)

def increment_counter():
    global counter
    print(f"Button pressed! Current count: {counter}")
    counter += 1

# Function to handle button press
def handle_button_press():
    # lcd_backlight_on()
    lcd_backlight_off()
    global button_press_count
    global button_press_count1
    global button_held
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW and not button_held:
            with lock:
                button_press_count += 1
                #print(f"Button Pressed! Count: {button_press_count}")
                increment_counter()
                formatted_value = f'{button_press_count:03d}'
                lcd_set_cursor(0, 0)
                lcd_message(f"TIN {formatted_value}")
                lcd_set_cursor(0, 8)
                lcd_message(f"TOUT {button_press_count1}")

                # Example: Display "World" at row 1, column 0
                lcd_set_cursor(1, 0)
                lcd_message("PIN 12")
                lcd_set_cursor(1, 8)
                lcd_message("POUT 12")
                button_held = True  # Set the state to indicate the button is held
            time.sleep(0.3)  # Debounce delay

        if GPIO.input(BUTTON_PIN) == GPIO.HIGH and button_held:
            button_held = False  # Reset the state when the button is released
            
        if GPIO.input(BUTTON_PIN1) == GPIO.LOW:
            with lock:
                button_press_count = 0
                button_press_count1 = 0
                print(f"Button Pressed! Count: {button_press_count1}")
                lcd_set_cursor(0, 0)
                formatted_value = f'{button_press_count:03d}'
                lcd_message(f"TIN {formatted_value}")
                lcd_set_cursor(0, 8)
                lcd_message(f"TOUT {button_press_count1}")

                # Example: Display "World" at row 1, column 0
                lcd_set_cursor(1, 0)
                lcd_message("PIN 12")
                lcd_set_cursor(1, 8)
                lcd_message("POUT 12")
            time.sleep(0.3)  # Debounce delay

# Main Program

lcd_init()  # Initialize the LCD

# Create and start thread for button press monitoring
button_thread = threading.Thread(target=handle_button_press)
button_thread.start()

# Keep the main thread running
try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    lcd_byte(0x01, LCD_CMD | LCD_BACKLIGHT)  # Clear the display with backlight
    GPIO.cleanup()
# Example: Display "Hello" at row 0, column 5


