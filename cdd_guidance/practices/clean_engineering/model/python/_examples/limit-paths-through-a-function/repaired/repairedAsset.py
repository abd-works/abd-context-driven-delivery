class Catalogue:
    """Prices each kind of thing the shop sells."""

    def __init__(self, prices: dict[str, int]) -> None:
        self._prices = prices

    def price_of(self, kind: str) -> int:
        return self._prices.get(kind, 0)
