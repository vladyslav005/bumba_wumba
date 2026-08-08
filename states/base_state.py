"""Base class for application states."""



class BaseState():

    def enter(self, app) -> None:
        """Execute logic when entering the state."""

    def exit(self, app) -> None:
        """Execute logic when leaving the state."""

    def update(self, app) -> None:
        """Run state-specific updates."""
