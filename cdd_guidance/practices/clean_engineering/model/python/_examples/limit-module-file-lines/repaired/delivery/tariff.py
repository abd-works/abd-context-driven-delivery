"""The tariff of every region, in a file of its own."""


class Tariff:
    def north(self) -> int:
        return 1

    def south(self) -> int:
        return 2

    def east(self) -> int:
        return 3

    def west(self) -> int:
        return 4

    def islands(self) -> int:
        return 5

    def highlands(self) -> int:
        return 6

    def coast(self) -> int:
        return 7

    def valley(self) -> int:
        return 8

    def city(self) -> int:
        return 9

    def border(self) -> int:
        return 10
