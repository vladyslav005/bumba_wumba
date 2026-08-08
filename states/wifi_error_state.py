from states.base_state import BaseState
from states.time_sync_state import TimeSyncState
import time
from machine import Pin


class WifiErrorState(BaseState):

    def __init__(self, message):
        self.message = message
        self.button_pin = None
        self.last_pin_value = 1
        self.blink_on = False
        self.last_blink = 0
        self.blink_interval = 500

    def enter(self, app):
        # Show error message and instructions to retry
        app.display.show(self.message[:16], "Press GP22 to retry")

        # Configure button on GP22 (assume active-low with pull-up)
        self.button_pin = Pin(22, Pin.IN, Pin.PULL_UP)
        self.last_pin_value = self.button_pin.value()

        # Start blinking red indicator
        self.blink_on = False
        self.last_blink = time.ticks_ms()
        app.rgb.off()

    def update(self, app):
        # Blink red LED to indicate WiFi error
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_blink) >= self.blink_interval:
            self.last_blink = now
            self.blink_on = not self.blink_on

            if self.blink_on:
                app.rgb.red()
            else:
                app.rgb.off()

        # Detect button press (falling edge) to attempt reconnect
        try:
            val = self.button_pin.value()
        except Exception:
            # If pin read fails, just skip
            val = self.last_pin_value

        if self.last_pin_value == 1 and val == 0:
            # simple debounce
            time.sleep_ms(20)
            if self.button_pin.value() == 0:
                app.display.show("Reconnecting...", "Please wait...")

                success = app.wifi.connect()

                if success:
                    app.rgb.green()
                    app.change_state(TimeSyncState())
                else:
                    # show retry failed and continue blinking
                    app.display.show(self.message[:16], "Retry failed")

        self.last_pin_value = val

    def exit(self, app):
        app.rgb.off()
