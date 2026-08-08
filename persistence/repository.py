"""Simple persistence repository stub."""


class Repository:
    """Temporary in-memory repository placeholder."""

    def __init__(self) -> None:
        self.data = {}

    def save(self, key: str, value: object) -> None:
        self.data[key] = value

    def load(self, key: str) -> object:
        return self.data.get(key)
