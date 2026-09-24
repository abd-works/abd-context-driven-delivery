from __future__ import annotations



class ActionRound:
    @property
    def turn_order(self) -> object:
        ...

    @property
    def roll_initiative(self) -> object:
        ...
