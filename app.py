"""Application entry point for the Super Bumba project."""


class App:
    """Simple application shell for the state machine architecture."""

    def __init__(self) -> None:
        self.current_state = None

    def run(self) -> None:
        """Start the application loop."""
        print("Super Bumba app started")


if __name__ == "__main__":
    App().run()
