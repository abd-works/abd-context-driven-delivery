from __future__ import annotations


class Check:




    @property
    def trait(self) -> object:
        ...


    @property
    def dc(self) -> object:
        ...


    @property
    def circumstance_modifier(self) -> object:
        ...


    def resolve(self) -> None:
        ...


    def resolve_graded(self) -> None:
        ...
