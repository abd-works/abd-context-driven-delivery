"""The rate of each kind of goods is data the class looks up, so its total complexity is 1."""

RATES = {"book": 1, "film": 2, "game": 3, "toy": 4, "food": 5, "wine": 6, "plant": 7, "tool": 8, "shoe": 9, "coat": 10, "lamp": 11, "desk": 12, "sofa": 13, "rug": 14, "bike": 15, "tent": 16}


class ShippingRate:
    def of(self, kind: str) -> int:
        return RATES.get(kind, 0)
