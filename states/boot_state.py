"""Boot state implementation."""

from states.base_state import BaseState


class BootState(BaseState):
    """Initial startup state."""

    def enter(self) -> None:
        print("Entering boot state")

    def exit(self) -> None:
        print("Exiting boot state")

    def update(self) -> None:
        print("Boot state update")
