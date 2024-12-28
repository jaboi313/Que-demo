from pyfirmata2 import Arduino
import time
arduino = Arduino(Arduino.AUTODETECT)
arduino.samplingOn(100)

def button_in_callback(value) -> None:
    """Detect button press and increase 'person_amount' by 1"""
    global person_amount
    if value and person_amount < (person_amount_max * multiplier):
        person_amount += 1

def button_out_callback(value) -> None:
    """Detect button press and lower 'person_amount' by 1"""
    global person_amount
    if value and person_amount > 0:
        person_amount -= 1

def set_leds() -> None:
    """Enable and disable led's based on 'traffic_light' state"""
    match traffic_light:
        case 'red':
            Led_red.write(1)
            Led_orange.write(0)
            Led_green.write(0)
        case 'orange':
            Led_red.write(0)
            Led_orange.write(1)
            Led_green.write(0)
        case 'green':
            Led_red.write(0)
            Led_orange.write(0)
            Led_green.write(1)

def set_gate() -> None:
    """Move servo based on 'gate' state"""
    match gate:
        case 'open':
            Servo.write(90)
        case 'closed':
            Servo.write(0)


global que_state
# Example :
# 1.0 = 160
# 0.1 = 16
multiplier:float = 0.1

LCD_PRINT:hex = 0x01
LCD_CLEAR:hex = 0x02
LCD_SET_CURSOR:hex = 0x03

title_text:str = "Aantal mensen :"

que_state:str = 'LEEG'      # Start state
person_amount:int = 0       # Start amount
person_amount_max:int = 160

current_time:time = time.time()
last_check_time:time = current_time
check_time_interval:float = 0.2

def setup() -> None:
    """
    Declare all ports and type of ports 
    - See 'get_pin' docstring
    - For button register callback with callback function, Also enable reporting    
    """
    global Button_in, Button_out, Led_red, Led_orange, Led_green, Servo
   
    Button_in = arduino.get_pin("d:6:i")
    Button_out = arduino.get_pin("d:5:i")

    Button_in.register_callback(button_in_callback)
    Button_out.register_callback(button_out_callback)

    Button_in.enable_reporting()
    Button_out.enable_reporting()

    Led_red = arduino.get_pin("d:4:o")
    Led_orange = arduino.get_pin("d:3:o")
    Led_green = arduino.get_pin("d:2:o")

    Servo = arduino.get_pin("d:9:s")

def convert_message(text:str) -> bytes:
    """
        Convert the string to bytes
        - Args:
            text (str): text to be converted
        - Returns:
            bytes: converted text
    """
    message_bytes = [ord(char) for char in str(text)]
    return message_bytes

def clear_screen() -> None:
    """Clears the LCD screen"""
    arduino.send_sysex(LCD_CLEAR, [])

def print_message(text:str, cursor_start:int, regel:int) -> None:
    """
        Displays the text at the specified x & y. 
        If text exceeds LCD max then text is not wrapped around or displayed a layer below (LCD behaviour)
        - Args:
            text (str): text to be displayed
            cursor_start (int): horizontal starting point of text, starts at 0
            regel (int): vertical starting point of text, starts at 0
    """
    arduino.send_sysex(LCD_SET_CURSOR, [cursor_start, regel])
    arduino.send_sysex(LCD_PRINT, convert_message(text))

def check_state() -> None:
    """Checks current 'que_state' and changes 'gate' state, 'state_text' & 'traffic_light' state"""
    global traffic_light, gate, state_text, que_state
    match que_state:
        case 'LEEG':
            gate = 'open'
            state_text = "LEEG"
            traffic_light = 'green'
            if person_amount > 0:
                que_state = 'BIJNA LEEG'
        case 'BIJNA LEEG':
            gate = 'open'
            state_text = "BIJNA LEEG"
            traffic_light = 'green'
            if person_amount < 1:
                que_state = 'LEEG'
            elif person_amount > ((person_amount_max * 0.125) * multiplier):
                que_state = 'REDELIJK LEEG'                
        case 'REDELIJK LEEG':
            gate = 'open'
            state_text = "REDELIJK LEEG"
            traffic_light = 'green'
            if person_amount < ((person_amount_max * 0.13125) * multiplier):
                que_state = 'BIJNA LEEG'
            elif person_amount > ((person_amount_max * 0.3125) * multiplier):
                que_state = 'MATIG LEEG'  
        case 'MATIG LEEG':
            gate = 'open'
            state_text = "MATIG LEEG"
            traffic_light = 'green'
            if person_amount < ((person_amount_max * 0.31875) * multiplier):
                que_state = 'REDELIJK LEEG'
            elif person_amount > (((person_amount_max * 0.5) - 1) * multiplier):
                que_state = 'HALF VOL/LEEG'  
        case 'HALF VOL/LEEG':
            gate = 'open'
            state_text = "HALF VOL/LEEG"
            traffic_light = 'orange'
            if person_amount < ((person_amount_max * 0.5) * multiplier):
                que_state = 'MATIG LEEG'
            elif person_amount > ((person_amount_max * 0.5) * multiplier):
                que_state = 'MATIG VOL'  
        case 'MATIG VOL':
            gate = 'open'
            state_text = "MATIG VOL"
            traffic_light = 'orange'
            if person_amount < (((person_amount_max * 0.5) + 1) * multiplier):
                que_state = 'HALF VOL/LEEG'
            elif person_amount > ((person_amount_max * 0.6875) * multiplier):
                que_state = 'REDELIJK VOL'  
        case 'REDELIJK VOL':
            gate = 'open'
            state_text = "REDELIJK VOL"
            traffic_light = 'orange'
            if person_amount < ((person_amount_max * 0.69375) * multiplier):
                que_state = 'MATIG VOL'
            elif person_amount > ((person_amount_max * 0.875) * multiplier):
                que_state = 'BIJNA VOL'  
        case 'BIJNA VOL':
            gate = 'open'
            state_text = "BIJNA VOL"
            traffic_light = 'red'
            if person_amount < ((person_amount_max * 0.88125) * multiplier):
                que_state = 'REDELIJK VOL'
            elif person_amount > ((person_amount_max - 1) * multiplier):
                que_state = 'VOL'  
        case 'VOL':
            gate = 'closed'
            state_text = "VOL"
            traffic_light = 'red'
            if person_amount < (person_amount_max * multiplier):
                que_state = 'BIJNA VOL'

def update_screen() -> None:
    """Update the screen based on time interval"""
    global last_check_time
    current_time = time.time()
    if current_time - last_check_time >= check_time_interval:
        clear_screen()
        print_message(title_text, 0, 0)
        print_message(state_text, (len(str(person_amount)) + 1), 1)
        print_message(person_amount, 0, 1)
        last_check_time = current_time

setup()

while True:
    check_state()
    set_gate()
    update_screen()
    set_leds()