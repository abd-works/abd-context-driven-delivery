from __future__ import annotations



class Flaw:
    @property
    def per_rank(self) -> object:
        ...

    @property
    def removable(self) -> object:
        ...
