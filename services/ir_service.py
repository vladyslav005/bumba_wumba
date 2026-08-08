from machine import Pin
import time
import micropython


micropython.alloc_emergency_exception_buf(100)


class IRService:

    def __init__(self, pin=16):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)

        # NEC frame needs about 67 pulse durations
        self.timings = [0] * 70

        self.count = 0
        self.last_edge = 0
        self.receiving = False
        self.frame_ready = False

        self.pin.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            handler=self._irq_handler
        )

    def _irq_handler(self, pin):
        if self.frame_ready:
            return

        now = time.ticks_us()

        if self.last_edge == 0:
            self.last_edge = now
            return

        duration = time.ticks_diff(now, self.last_edge)
        self.last_edge = now

        # Large gap = beginning of a new IR frame
        if duration > 15000:
            self.count = 0
            self.receiving = True
            return

        if not self.receiving:
            # First falling edge starts the frame
            if pin.value() == 0:
                self.count = 0
                self.receiving = True
            return

        if self.count < len(self.timings):
            self.timings[self.count] = duration
            self.count += 1

        # NEC frame: leader + 32 bits + final pulse
        if self.count >= 67:
            self.receiving = False
            self.frame_ready = True

    def read(self):
        if not self.frame_ready:
            return None

        self.frame_ready = False

        return self._decode_nec()

    def _decode_nec(self):
        # NEC leader:
        # ~9000 us LOW
        # ~4500 us HIGH
        if not (7000 < self.timings[0] < 10000):
            return None

        if not (3500 < self.timings[1] < 5500):
            return None

        value = 0

        for bit_index in range(32):
            low = self.timings[2 + bit_index * 2]
            high = self.timings[3 + bit_index * 2]

            # Every bit starts with about 560 us LOW
            if not (300 < low < 900):
                return None

            if 300 < high < 900:
                bit = 0

            elif 1200 < high < 2200:
                bit = 1

            else:
                return None

            value |= bit << bit_index

        address = value & 0xFF
        address_inverse = (value >> 8) & 0xFF
        command = (value >> 16) & 0xFF
        command_inverse = (value >> 24) & 0xFF

        # Validate command
        if (command ^ command_inverse) != 0xFF:
            return None

        return {
            "address": address,
            "command": command
        }