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

    @property
    def resolve(self) -> object:
        ...

    @property
    def resolve_graded(self) -> object:
        ...
