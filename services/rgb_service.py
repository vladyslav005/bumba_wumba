from machine import Pin
import neopixel


class RGBService:

    def __init__(self, pin=28):
        self.pixel = neopixel.NeoPixel(
            Pin(pin),
            1
        )

        self.off()

    def set_color(self, red, green, blue):
        self.pixel[0] = (
            red,
            green,
            blue
        )

        self.pixel.write()

    def green(self):
        self.set_color(0, 30, 0)

    def yellow(self):
        self.set_color(30, 20, 0)

    def red(self):
        self.set_color(30, 0, 0)

    def off(self):
        self.set_color(0, 0, 0)