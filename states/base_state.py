"""Base class for application states."""

from abc import ABC, abstractmethod


class BaseState(ABC):
    """Represents a single state in the application lifecycle."""

    @abstractmethod
    def enter(self) -> None:
        """Execute logic when entering the state."""

    @abstractmethod
    def exit(self) -> None:
        """Execute logic when leaving the state."""

    @abstractmethod
    def update(self) -> None:
        """Run state-specific updates."""
