"""Home state implementation."""

from states.base_state import BaseState


class HomeState(BaseState):
    """Main home screen state."""

    def enter(self) -> None:
        print("Entering home state")

    def exit(self) -> None:
        print("Exiting home state")

    def update(self) -> None:
        print("Home state update")
