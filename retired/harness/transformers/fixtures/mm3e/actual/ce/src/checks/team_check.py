from __future__ import annotations

from .check import Check

class TeamCheck(Check):




    @property
    def helpers(self) -> object:
        ...


    def resolve(self) -> None:
        ...
