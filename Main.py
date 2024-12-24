from pyfirmata2 import Arduino
arduino = Arduino(Arduino.AUTODETECT)

lcd_hor:int = 16
lcd_ver:int = 2

LCD_PRINT:hex = 0x01
LCD_CLEAR:hex = 0x02
LCD_SET_CURSOR:hex = 0x03

regel1:str = "1234567890123456"
regel2:str = "abcdefghijklmnop"

def convert_message(text:str) -> bytes:
    """
            Convert the string to bytes
        Args:
            text (str): text to be converted
        Returns:
            bytes: converted text
    """
    message_bytes = [ord(char) for char in text]
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

print_message(regel1, 0, 0)
print_message(regel2, 0, 1)

arduino.exit()