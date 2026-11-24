"""Every kind of goods is a branch of its own, so the one class of the module has a total complexity of 17."""


class ShippingRate:
    def of(self, kind: str) -> int:
        if kind == "book":
            return 1
        if kind == "film":
            return 2
        if kind == "game":
            return 3
        if kind == "toy":
            return 4
        if kind == "food":
            return 5
        if kind == "wine":
            return 6
        if kind == "plant":
            return 7
        if kind == "tool":
            return 8
        if kind == "shoe":
            return 9
        if kind == "coat":
            return 10
        if kind == "lamp":
            return 11
        if kind == "desk":
            return 12
        if kind == "sofa":
            return 13
        if kind == "rug":
            return 14
        if kind == "bike":
            return 15
        if kind == "tent":
            return 16
        return 0
