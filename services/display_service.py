from machine import I2C, Pin
import time


class DisplayService:
    LCD_ADDR = 0x27

    LCD_BACKLIGHT = 0x08
    ENABLE = 0x04
    RS = 0x01

    def __init__(self, sda_pin=4, scl_pin=5):
        self.i2c = I2C(
            0,
            sda=Pin(sda_pin),
            scl=Pin(scl_pin),
            freq=100000
        )

        self._init_lcd()

    def _write_byte(self, value):
        self.i2c.writeto(
            self.LCD_ADDR,
            bytes([value | self.LCD_BACKLIGHT])
        )

    def _pulse_enable(self, value):
        self._write_byte(value | self.ENABLE)
        time.sleep_us(1)

        self._write_byte(value & ~self.ENABLE)
        time.sleep_us(50)

    def _write_nibble(self, value):
        self._write_byte(value)
        self._pulse_enable(value)

    def _send(self, value, mode=0):
        high = mode | (value & 0xF0)
        low = mode | ((value << 4) & 0xF0)

        self._write_nibble(high)
        self._write_nibble(low)

    def command(self, value):
        self._send(value, 0)

    def write_char(self, char):
        self._send(ord(char), self.RS)

    def write(self, text):
        for char in str(text):
            self.write_char(char)

    def clear(self):
        self.command(0x01)
        time.sleep_ms(2)

    def set_cursor(self, row, column=0):
        if row == 0:
            address = 0x00
        else:
            address = 0x40

        self.command(0x80 | (address + column))

    def show(self, line1="", line2=""):
        # Ensure we never send more than 16 characters per line to the display.
        # Truncate rather than raising so callers don't crash when strings are
        # longer than the hardware supports.
        line1 = str(line1)[:16]
        line2 = str(line2)[:16]

        self.clear()

        self.set_cursor(0, 0)
        self.write(line1)

        self.set_cursor(1, 0)
        self.write(line2)

    def _init_lcd(self):
        time.sleep_ms(50)

        # Initialization into 4-bit mode
        self._write_nibble(0x30)
        time.sleep_ms(5)

        self._write_nibble(0x30)
        time.sleep_us(150)

        self._write_nibble(0x30)
        self._write_nibble(0x20)

        # 4 bit, 2 lines, 5x8 font
        self.command(0x28)

        # Display ON, cursor OFF
        self.command(0x0C)

        # Entry mode
        self.command(0x06)

        self.clear()