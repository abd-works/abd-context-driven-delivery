"""The zones, in a file of their own."""


class Zone:
    def __init__(self, name: str) -> None:
        self._name = name

    def name(self) -> str:
        return self._name
