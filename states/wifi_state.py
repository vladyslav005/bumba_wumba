from states.base_state import BaseState
from states.time_sync_state import TimeSyncState
from states.wifi_error_state import WifiErrorState


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

        # Use retry-capable connect to improve robustness
        success = app.wifi.connect_with_retries(retries=3, timeout_seconds=10)

        if success:
            app.change_state(TimeSyncState())
        else:
            app.change_state(
                WifiErrorState("WiFi connection failed")
            )

    def exit(self, app):
        print("WiFi state finished")