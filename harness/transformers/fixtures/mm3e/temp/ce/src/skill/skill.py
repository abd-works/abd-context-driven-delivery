from __future__ import annotations







class Skill(Trait):
    @property
    def linked_ability(self) -> object:
        ...

    @property
    def trained_only(self) -> object:
        ...

    @property
    def assign_ranks(self) -> object:
        ...

    @property
    def make_check(self) -> object:
        ...

    @property
    def resolve_untrained(self) -> object:
        ...
