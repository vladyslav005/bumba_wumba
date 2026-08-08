"""Time synchronization state implementation."""

from states.base_state import BaseState


class TimeSyncState(BaseState):
    """Handles time synchronization logic."""

    def enter(self) -> None:
        print("Entering time sync state")

    def exit(self) -> None:
        print("Exiting time sync state")

    def update(self) -> None:
        print("Time sync state update")
