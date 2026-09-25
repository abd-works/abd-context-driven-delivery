from __future__ import annotations


class Attack:




    @property
    def attack_bonus(self) -> object:
        ...


    @property
    def defense_class(self) -> object:
        ...


    def resolve(self) -> None:
        ...


    def confirm_critical(self) -> None:
        ...
