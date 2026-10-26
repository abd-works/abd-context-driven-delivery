from __future__ import annotations



class ImposedCondition:
    @property
    def condition(self) -> object:
        ...

    @property
    def source(self) -> object:
        ...

    @property
    def active(self) -> object:
        ...
