from __future__ import annotations



class Attack:
    @property
    def attack_bonus(self) -> object:
        ...

    @property
    def defense_class(self) -> object:
        ...

    @property
    def resolve(self) -> object:
        ...

    @property
    def confirm_critical(self) -> object:
        ...
