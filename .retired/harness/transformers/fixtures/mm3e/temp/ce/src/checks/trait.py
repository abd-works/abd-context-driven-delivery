from __future__ import annotations



class Trait:
    @property
    def character(self) -> object:
        ...

    @property
    def trait_name(self) -> object:
        ...

    @property
    def purchased_rank(self) -> object:
        ...

    @property
    def effective_rank(self) -> object:
        ...

    def real_world_value(self, type) -> None:
        ...

    def add_rank(self, other, type) -> None:
        ...

    def perform_check(self, dc) -> None:
        ...
