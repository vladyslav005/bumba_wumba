import time

from states.base_state import BaseState
from states.wifi_state import WiFiState


class BootState(BaseState):

    def __init__(self):
        self.started_at = 0

    def enter(self, app):
        print("System booting...")

        app.display.show(
            "Bumba Wumba",
            "Starting..."
        )

        self.started_at = time.ticks_ms()

    def update(self, app):
        if time.ticks_diff(
            time.ticks_ms(),
            self.started_at
        ) >= 1000:

            app.change_state(WiFiState())

    def exit(self, app):
        print("Boot complete")