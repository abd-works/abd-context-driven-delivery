from __future__ import annotations

from checks.trait import Trait

class Ability(Trait):




    @property
    def natural_rank(self) -> object:
        ...


    @property
    def enhanced_rank(self) -> object:
        ...


    def set_rank(self, purchased_rank) -> None:
        ...


    def cascade_dependents(self) -> None:
        ...


    def apply_absent_restrictions(self) -> None:
        ...


    def apply_debilitated(self) -> None:
        ...
