from states.base_state import BaseState
from states.time_sync_state import TimeSyncState
from states.error_state import ErrorState


class WiFiState(BaseState):

    def __init__(self):
        self.connection_attempted = False

    def enter(self, app):
        app.display.show(
            "Connecting WiFi",
            "Please wait..."
        )

    def update(self, app):
        if self.connection_attempted:
            return

        self.connection_attempted = True

        success = app.wifi.connect()

        if success:
            app.change_state(TimeSyncState())
        else:
            app.change_state(
                ErrorState("WiFi connection failed")
            )

    def exit(self, app):
        print("WiFi state finished")