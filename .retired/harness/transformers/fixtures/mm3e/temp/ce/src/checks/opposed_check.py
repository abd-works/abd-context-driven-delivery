from __future__ import annotations







class OpposedCheck(Check):
    @property
    def opponent(self) -> object:
        ...

    @property
    def is_passive(self) -> object:
        ...

    @property
    def resolve(self) -> object:
        ...
