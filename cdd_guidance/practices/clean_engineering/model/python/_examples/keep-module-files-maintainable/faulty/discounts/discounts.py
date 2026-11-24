"""Each kind of customer has its own method, each a ladder of the same thresholds written out again, so the file is
long, branching and repetitive: its maintainability index is under 20."""


class Discounts:
    def __init__(self, extra: int) -> None:
        self._extra = extra

    def student(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 0 + self._extra) // 100
        if total >= 500:
            return total * (20 + 0 + self._extra) // 100
        if total >= 250:
            return total * (15 + 0 + self._extra) // 100
        if total >= 100:
            return total * (10 + 0 + self._extra) // 100
        if total >= 50:
            return total * (5 + 0 + self._extra) // 100
        if total >= 20:
            return total * (2 + 0 + self._extra) // 100
        return 0

    def senior(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 1 + self._extra) // 100
        if total >= 500:
            return total * (20 + 1 + self._extra) // 100
        if total >= 250:
            return total * (15 + 1 + self._extra) // 100
        if total >= 100:
            return total * (10 + 1 + self._extra) // 100
        if total >= 50:
            return total * (5 + 1 + self._extra) // 100
        if total >= 20:
            return total * (2 + 1 + self._extra) // 100
        return 0

    def staff(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 2 + self._extra) // 100
        if total >= 500:
            return total * (20 + 2 + self._extra) // 100
        if total >= 250:
            return total * (15 + 2 + self._extra) // 100
        if total >= 100:
            return total * (10 + 2 + self._extra) // 100
        if total >= 50:
            return total * (5 + 2 + self._extra) // 100
        if total >= 20:
            return total * (2 + 2 + self._extra) // 100
        return 0

    def trade(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 3 + self._extra) // 100
        if total >= 500:
            return total * (20 + 3 + self._extra) // 100
        if total >= 250:
            return total * (15 + 3 + self._extra) // 100
        if total >= 100:
            return total * (10 + 3 + self._extra) // 100
        if total >= 50:
            return total * (5 + 3 + self._extra) // 100
        if total >= 20:
            return total * (2 + 3 + self._extra) // 100
        return 0

    def charity(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 4 + self._extra) // 100
        if total >= 500:
            return total * (20 + 4 + self._extra) // 100
        if total >= 250:
            return total * (15 + 4 + self._extra) // 100
        if total >= 100:
            return total * (10 + 4 + self._extra) // 100
        if total >= 50:
            return total * (5 + 4 + self._extra) // 100
        if total >= 20:
            return total * (2 + 4 + self._extra) // 100
        return 0

    def school(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 5 + self._extra) // 100
        if total >= 500:
            return total * (20 + 5 + self._extra) // 100
        if total >= 250:
            return total * (15 + 5 + self._extra) // 100
        if total >= 100:
            return total * (10 + 5 + self._extra) // 100
        if total >= 50:
            return total * (5 + 5 + self._extra) // 100
        if total >= 20:
            return total * (2 + 5 + self._extra) // 100
        return 0

    def member(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 6 + self._extra) // 100
        if total >= 500:
            return total * (20 + 6 + self._extra) // 100
        if total >= 250:
            return total * (15 + 6 + self._extra) // 100
        if total >= 100:
            return total * (10 + 6 + self._extra) // 100
        if total >= 50:
            return total * (5 + 6 + self._extra) // 100
        if total >= 20:
            return total * (2 + 6 + self._extra) // 100
        return 0

    def partner(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 7 + self._extra) // 100
        if total >= 500:
            return total * (20 + 7 + self._extra) // 100
        if total >= 250:
            return total * (15 + 7 + self._extra) // 100
        if total >= 100:
            return total * (10 + 7 + self._extra) // 100
        if total >= 50:
            return total * (5 + 7 + self._extra) // 100
        if total >= 20:
            return total * (2 + 7 + self._extra) // 100
        return 0

    def reseller(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 8 + self._extra) // 100
        if total >= 500:
            return total * (20 + 8 + self._extra) // 100
        if total >= 250:
            return total * (15 + 8 + self._extra) // 100
        if total >= 100:
            return total * (10 + 8 + self._extra) // 100
        if total >= 50:
            return total * (5 + 8 + self._extra) // 100
        if total >= 20:
            return total * (2 + 8 + self._extra) // 100
        return 0

    def wholesale(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 9 + self._extra) // 100
        if total >= 500:
            return total * (20 + 9 + self._extra) // 100
        if total >= 250:
            return total * (15 + 9 + self._extra) // 100
        if total >= 100:
            return total * (10 + 9 + self._extra) // 100
        if total >= 50:
            return total * (5 + 9 + self._extra) // 100
        if total >= 20:
            return total * (2 + 9 + self._extra) // 100
        return 0

    def veteran(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 10 + self._extra) // 100
        if total >= 500:
            return total * (20 + 10 + self._extra) // 100
        if total >= 250:
            return total * (15 + 10 + self._extra) // 100
        if total >= 100:
            return total * (10 + 10 + self._extra) // 100
        if total >= 50:
            return total * (5 + 10 + self._extra) // 100
        if total >= 20:
            return total * (2 + 10 + self._extra) // 100
        return 0

    def family(self, total: int) -> int:
        if total >= 1000:
            return total * (25 + 11 + self._extra) // 100
        if total >= 500:
            return total * (20 + 11 + self._extra) // 100
        if total >= 250:
            return total * (15 + 11 + self._extra) // 100
        if total >= 100:
            return total * (10 + 11 + self._extra) // 100
        if total >= 50:
            return total * (5 + 11 + self._extra) // 100
        if total >= 20:
            return total * (2 + 11 + self._extra) // 100
        return 0

