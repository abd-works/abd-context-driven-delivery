from __future__ import annotations



class AttackTradeOff:
    @property
    def penalty_stat(self) -> object:
        ...

    @property
    def bonus_stat(self) -> object:
        ...

    @property
    def amount(self) -> object:
        ...
