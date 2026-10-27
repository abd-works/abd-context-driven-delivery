from __future__ import annotations

from .check import Check

class OpposedCheck(Check):




    @property
    def opponent(self) -> object:
        ...


    @property
    def is_passive(self) -> object:
        ...


    def resolve(self) -> None:
        ...
