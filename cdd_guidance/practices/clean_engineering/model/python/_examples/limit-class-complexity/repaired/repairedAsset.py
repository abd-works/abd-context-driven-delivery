class Pricing:
    """The one pricing rule every order takes."""

    def __init__(self, base: int) -> None:
        self._base = base

    def rule_0(self, value: int) -> int:
        if value == 0:
            return 0
        return self._base + value

