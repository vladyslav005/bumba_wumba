from states.base_state import BaseState
import time


FORWARD_BUTTON = 0x40
BACK_BUTTON = 0x44

IR_DEBOUNCE_MS = 300


class CarouselState(BaseState):

    def __init__(self):
        self.last_ir_time = 0

    def handle_navigation(self, app):
        result = app.ir.read()

        if result is None:
            return False

        now = time.ticks_ms()

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

        return False