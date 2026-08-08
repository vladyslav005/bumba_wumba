"""Wi-Fi state implementation."""

from states.base_state import BaseState


class WifiState(BaseState):
    """Handles Wi-Fi connectivity."""

    def enter(self) -> None:
        print("Entering wifi state")

    def exit(self) -> None:
        print("Exiting wifi state")

    def update(self) -> None:
        print("Wifi state update")
