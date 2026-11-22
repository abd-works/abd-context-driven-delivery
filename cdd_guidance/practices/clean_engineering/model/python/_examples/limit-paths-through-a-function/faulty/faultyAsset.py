class Catalogue:
    """Prices each kind of thing the shop sells."""

    def price_of(self, kind: str) -> int:
        if kind == "book":
            return 1
        if kind == "pen":
            return 2
        if kind == "ink":
            return 3
        if kind == "card":
            return 4
        if kind == "lamp":
            return 5
        if kind == "desk":
            return 6
        if kind == "chair":
            return 7
        if kind == "shelf":
            return 8
        if kind == "rug":
            return 9
        if kind == "clock":
            return 10
        if kind == "vase":
            return 11
        return 0
