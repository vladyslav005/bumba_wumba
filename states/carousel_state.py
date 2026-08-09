from states.base_state import BaseState
import time
from machine import Pin


FORWARD_BUTTON = 0x40
BACK_BUTTON = 0x44

IR_DEBOUNCE_MS = 300
GPIO_DEBOUNCE_MS = 200


class CarouselState(BaseState):

    def __init__(self):
        self.last_ir_time = 0
        self.last_gpio_time = 0
        self.gpio_buttons = {
            20: "next",
            22: "previous",
        }
        self.button_pins = {}
        self._init_gpio_buttons()

    def _init_gpio_buttons(self):
        for pin_number, direction in self.gpio_buttons.items():
            try:
                pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
                self.button_pins[pin_number] = {
                    "pin": pin,
                    "pressed_value": 0,
                    "last_value": pin.value(),
                }
            except Exception:
                pass

    def _read_gpio_button(self, pin_number):
        config = self.button_pins.get(pin_number)

        if config is None:
            return None

        pin = config["pin"]

        try:
            value = pin.value()
        except Exception:
            return None

        if value != config["last_value"]:
            time.sleep_ms(20)
            try:
                value = pin.value()
            except Exception:
                return None

        config["last_value"] = value

        if value == config["pressed_value"]:
            return True

        return False

    def handle_navigation(self, app):
        now = time.ticks_ms()

        result = app.ir.read()

        if result is not None:
            if time.ticks_diff(now, self.last_ir_time) < IR_DEBOUNCE_MS:
                return False

            self.last_ir_time = now

            command = result["command"]

            print("IR:", hex(command))

            if command == FORWARD_BUTTON:
                app.change_state(app.navigator.next(app.state))
                return True

            if command == BACK_BUTTON:
                app.change_state(app.navigator.previous(app.state))
                return True

        for pin_number in (20, 22):
            if time.ticks_diff(now, self.last_gpio_time) < GPIO_DEBOUNCE_MS:
                continue

            if self._read_gpio_button(pin_number):
                self.last_gpio_time = now

                if pin_number == 20:
                    app.change_state(app.navigator.next(app.state))
                else:
                    app.change_state(app.navigator.previous(app.state))

                return True

        return False