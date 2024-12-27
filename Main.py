from pyfirmata2 import Arduino
import time
arduino = Arduino(Arduino.AUTODETECT)
arduino.samplingOn(100)

def button_in_callback(value):
    global person_amount
    if value and person_amount < 160:
        person_amount += 1

def button_out_callback(value):
    global person_amount
    if value and person_amount > 0:
        person_amount -= 1

def set_leds():
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

def set_gate():
    match gate:
        case 'open':
            Servo.write(90)
        case 'closed':
            Servo.write(0)


global traffic_light, gate, que_state

LCD_PRINT:hex = 0x01
LCD_CLEAR:hex = 0x02
LCD_SET_CURSOR:hex = 0x03

title_text:str = "Aantal mensen :"
state_text:str = "LEEG"     # Start text

traffic_light:str = 'green' # Start state
gate:str = 'open'           # Start state
que_state:str = 'LEEG'      # Start state
person_amount:int = 0       # Start amount

current_time:time = time.time()
last_check_time:time = current_time
check_time_interval:float = 0.2

def setup():
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
        Args:
            text (str): text to be converted
        Returns:
            bytes: converted text
    """
    message_bytes = [ord(char) for char in str(text)]
    return message_bytes

def clear_screen():
    """CLear the LCD screen"""
    arduino.send_sysex(LCD_CLEAR, [])

def print_message(text:str, cursor_start:int, regel:int) -> None:
    """
            Displays the text at the specified x & y. 
            If text exceeds LCD max then text is not wrapped around or displayed a layer below (LCD behaviour)
        Args:
            text (str): text to be displayed
            cursor_start (int): horizontal starting point of text, starts at 0
            regel (int): vertical starting point of text, starts at 0
    """
    arduino.send_sysex(LCD_SET_CURSOR, [cursor_start, regel])
    arduino.send_sysex(LCD_PRINT, convert_message(text))

def check_state():
    global traffic_light, gate, state_text, que_state
    match que_state:
        case 'LEEG':
            state_text = "LEEG"
            traffic_light = 'green'
            if person_amount > 0:
                que_state = 'BIJNA LEEG'
        case 'BIJNA LEEG':
            state_text = "BIJNA LEEG"
            traffic_light = 'green'
            if person_amount < 1:
                que_state = 'LEEG'
            elif person_amount > 20:
                que_state = 'REDELIJK LEEG'                
        case 'REDELIJK LEEG':
            state_text = "REDELIJK LEEG"
            traffic_light = 'green'
            if person_amount < 21:
                que_state = 'BIJNA LEEG'
            elif person_amount > 50:
                que_state = 'MATIG LEEG'  
        case 'MATIG LEEG':
            state_text = "MATIG LEEG"
            traffic_light = 'green'
            if person_amount < 51:
                que_state = 'REDELIJK LEEG'
            elif person_amount > 79:
                que_state = 'HALF VOL/LEEG'  
        case 'HALF VOL/LEEG':
            state_text = "HALF VOL/LEEG"
            traffic_light = 'orange'
            if person_amount < 80:
                que_state = 'MATIG LEEG'
            elif person_amount > 80:
                que_state = 'MATIG VOL'  
        case 'MATIG VOL':
            state_text = "MATIG VOL"
            traffic_light = 'orange'
            if person_amount < 81:
                que_state = 'HALF VOL/LEEG'
            elif person_amount > 110:
                que_state = 'REDELIJK VOL'  
        case 'REDELIJK VOL':
            state_text = "REDELIJK VOL"
            traffic_light = 'orange'
            if person_amount < 111:
                que_state = 'MATIG VOL'
            elif person_amount > 140:
                que_state = 'BIJNA VOL'  
        case 'BIJNA VOL':
            gate = 'open'
            state_text = "BIJNA VOL"
            traffic_light = 'red'
            if person_amount < 141:
                que_state = 'REDELIJK VOL'
            elif person_amount > 159:
                que_state = 'VOL'  
        case 'VOL':
            gate = 'closed'
            state_text = "VOL"
            traffic_light = 'red'
            if person_amount < 160:
                que_state = 'BIJNA VOL'

def update_screen():
    global last_check_time
    current_time = time.time()
    if current_time - last_check_time >= check_time_interval:
        clear_screen()
        print_message(title_text, 0, 0)
        print_message(state_text, 3, 1)
        print_message(person_amount, 0, 1)
        last_check_time = current_time

setup()

while True:
    check_state()
    set_gate()
    update_screen()
    set_leds()