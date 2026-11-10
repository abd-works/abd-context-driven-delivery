"""
"""
from __future__ import annotations


class Measurement:
    """Looks up a trait rank as a real-world measure and converts combined ranks through that table."""

    # never add ranks as integers — convert through this table then convert back

    def lookup(self, rank: int, type: object) -> object:
        ...

    def rank_for(self, measure: object, type: object) -> int:
        ...

    def throwing_distance_rank(self, strength_rank: int, mass_rank: int) -> int:
        # -> Measurement.lookup
        # -> Measurement.rank_for
        ...

    def travel_distance_rank(self, time_rank: int, speed_rank: int) -> int:
        # -> Measurement.lookup
        # -> Measurement.rank_for
        ...

    def travel_time_rank(self, distance_rank: int, speed_rank: int) -> int:
        # -> Measurement.lookup
        # -> Measurement.rank_for
        ...
