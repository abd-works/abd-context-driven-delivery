from __future__ import annotations

from checks.trait import Trait

class Advantage(Trait):




    @property
    def category(self) -> object:
        ...


    @property
    def rank(self) -> object:
        ...


    def purchase(self) -> None:
        ...


    def apply(self) -> None:
        ...
