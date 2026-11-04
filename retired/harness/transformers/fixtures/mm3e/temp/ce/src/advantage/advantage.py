from __future__ import annotations







class Advantage(Trait):
    @property
    def category(self) -> object:
        ...

    @property
    def rank(self) -> object:
        ...

    @property
    def purchase(self) -> object:
        ...

    @property
    def apply(self) -> object:
        ...
