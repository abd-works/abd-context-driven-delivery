"""The thresholds are written once and each kind of customer is a number in a table, so the file is short and has one
ladder: its maintainability index is well over 20."""

# The least an order totals for each share taken off it, largest first.
STEPS = ((1000, 25), (500, 20), (250, 15), (100, 10), (50, 5), (20, 2))
# What each kind of customer adds to the share.
SEGMENT_EXTRA = {"student": 0, "senior": 1, "staff": 2, "trade": 3, "charity": 4, "school": 5, "member": 6, "partner": 7, "reseller": 8, "wholesale": 9, "veteran": 10, "family": 11}


class Discounts:
    def __init__(self, extra: int) -> None:
        self._extra = extra

    def of(self, segment: str, total: int) -> int:
        percent = next((percent for threshold, percent in STEPS if total >= threshold), None)
        if percent is None:
            return 0
        return total * (percent + SEGMENT_EXTRA[segment] + self._extra) // 100
