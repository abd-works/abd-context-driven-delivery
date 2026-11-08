from __future__ import annotations

from checks.trait import Trait

class Effect(Trait):




    @property
    def action(self) -> object:
        ...


    @property
    def range(self) -> object:
        ...


    @property
    def duration(self) -> object:
        ...


    @property
    def base_cost_per_rank(self) -> object:
        ...


    def resolve(self) -> None:
        ...
