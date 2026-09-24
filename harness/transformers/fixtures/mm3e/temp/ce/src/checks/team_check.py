from __future__ import annotations







class TeamCheck(Check):
    @property
    def helpers(self) -> object:
        ...

    @property
    def resolve(self) -> object:
        ...
