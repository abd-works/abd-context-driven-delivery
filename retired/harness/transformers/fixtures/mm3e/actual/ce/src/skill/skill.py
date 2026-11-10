from __future__ import annotations

from checks.trait import Trait

class Skill(Trait):




    @property
    def linked_ability(self) -> object:
        ...


    @property
    def trained_only(self) -> object:
        ...


    def assign_ranks(self, purchased_rank) -> None:
        ...


    def make_check(self, dc) -> None:
        ...


    def resolve_untrained(self) -> None:
        ...
