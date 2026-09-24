from __future__ import annotations



class Measurement:
    def lookup(self, rank, type) -> None:
        ...

    def rank_for(self, measure, type) -> None:
        ...

    def throwing_distance_rank(self, strength_rank, mass_rank) -> None:
        ...

    def travel_distance_rank(self, time_rank, speed_rank) -> None:
        ...

    def travel_time_rank(self, distance_rank, speed_rank) -> None:
        ...
