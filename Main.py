from pyfirmata2 import Arduino
import time
from Wachtrijtheorie import calculate_Total, calculate_diff
arduino = Arduino(Arduino.AUTODETECT)
arduino.samplingOn(100)

def button_in_callback(value:bool) -> None:
    """Detect button press and increase 'person_amount' by 1"""
    global person_amount
    if value and person_amount < (person_amount_max * multiplier):
        person_amount += 1
        if queue_enable:
            queue.append(time.time())

def button_out_callback(value:bool) -> None:
    """Detect button press and lower 'person_amount' by 1"""
    global person_amount
    if value and person_amount > 0:
        person_amount -= 1
        if queue_enable:
            exit_time = time.time()
            exit_times.append(exit_time)

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
time_multiplier:float = 0.1

lcd_columns:int = 20

LCD_PRINT:hex = 0x01
LCD_CLEAR:hex = 0x02
LCD_SET_CURSOR:hex = 0x03

title_text:str = "Aantal mensen :"
wait_time_title_text:str = "Wacht tijd :"

que_state:str = 'LEEG'      # Start state
person_amount:int = 0       # Start amount
person_amount_max:int = 160

queue_enable:bool = True
wait_time:int = 0           # Start amount
queue:list = []
exit_time:float = 0
exit_times:list = []

avg_entries_per_minute:float = 0
avg_exits_per_minute:float = 0

current_time:time = time.time()
last_check_time:time = current_time
check_time_interval:float = 0.2

def calculate() -> None:
    """Calculate avarage entries per minute and avarage exits per minute"""
    global avg_entries_per_minute, avg_exits_per_minute
    AVERAGING_TIME:float = 60.0
    
    current_time:time = time.time()
    count:int = 0
    i = len(queue) - 1
    while i >= 0 and current_time - queue[i] < (AVERAGING_TIME  * time_multiplier):
        count += 1
        i -= 1

    avg_entries_per_minute = count / AVERAGING_TIME * 60.0

    count_:int = 0
    i = len(exit_times) - 1
    while i >= 0 and current_time - exit_times[i] < (AVERAGING_TIME  * time_multiplier):
        count_ += 1
        i -= 1

    avg_exits_per_minute = count_ / AVERAGING_TIME * 60.0

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

def print_message(text:str, row:int, cursor_start:int=None, centered:bool=False, lcd_columns:int=None) -> None:
    """
        Displays the text at the specified x & y. 
        If text exceeds LCD max then text is not wrapped around or displayed a layer below (LCD behaviour)
        - Args:
            text (str): text to be displayed
            cursor_start (int): horizontal starting point of text, starts at 0
            row (int): vertical starting point of text, starts at 0
            centered (bool): if True text is centered on screen based on 'lcd_columns'
            lcd_columns (int): amount of columns the lcd has
    """
    if centered:
        arduino.send_sysex(LCD_SET_CURSOR, [int((lcd_columns/2)-((len(str(text)))/2)), row])
    else:    
        arduino.send_sysex(LCD_SET_CURSOR, [cursor_start, row])
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
            if person_amount < (((person_amount_max * 0.125) + 1) * multiplier):
                que_state = 'BIJNA LEEG'
            elif person_amount > ((person_amount_max * 0.3125) * multiplier):
                que_state = 'MATIG LEEG'  
        case 'MATIG LEEG':
            gate = 'open'
            state_text = "MATIG LEEG"
            traffic_light = 'green'
            if person_amount < (((person_amount_max * 0.3125) + 1) * multiplier):
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
            if person_amount < (((person_amount_max * 0.6875) + 1) * multiplier):
                que_state = 'MATIG VOL'
            elif person_amount > ((person_amount_max * 0.875) * multiplier):
                que_state = 'BIJNA VOL'  
        case 'BIJNA VOL':
            gate = 'open'
            state_text = "BIJNA VOL"
            traffic_light = 'red'
            if person_amount < (((person_amount_max * 0.875) + 1)* multiplier):
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
        print(avg_entries_per_minute)
        print("------------------")
        print(avg_exits_per_minute)
        print("------------------")
        print("------------------")
        clear_screen()
        print_message(title_text + " " + str(person_amount), row=0, cursor_start=0)
        if queue_enable:
            if person_amount > 0:
                print_message(wait_time_title_text + " " + str(calculate_diff(avg_entries_per_minute, avg_exits_per_minute)), row=1, cursor_start=0)
            else:
                print_message(wait_time_title_text + " " + str(wait_time), row=1, cursor_start=0)
            print_message(state_text, row=3, centered=True, lcd_columns=lcd_columns)
        else:
            print_message(state_text, row=2, centered=True, lcd_columns=lcd_columns)
        last_check_time = current_time

setup()

while True:
    check_state()
    set_gate()
    update_screen()
    calculate()
    set_leds()