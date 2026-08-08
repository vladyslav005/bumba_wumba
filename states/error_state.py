"""Error state implementation."""

from states.base_state import BaseState


class ErrorState(BaseState):
    """Handles error recovery presentation."""

    def enter(self) -> None:
        print("Entering error state")

    def exit(self) -> None:
        print("Exiting error state")

    def update(self) -> None:
        print("Error state update")
