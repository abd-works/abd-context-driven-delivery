from __future__ import annotations







class Ability(Trait):
    @property
    def natural_rank(self) -> object:
        ...

    @property
    def enhanced_rank(self) -> object:
        ...

    @property
    def set_rank(self) -> object:
        ...

    @property
    def cascade_dependents(self) -> object:
        ...

    @property
    def apply_absent_restrictions(self) -> object:
        ...

    @property
    def apply_debilitated(self) -> object:
        ...
