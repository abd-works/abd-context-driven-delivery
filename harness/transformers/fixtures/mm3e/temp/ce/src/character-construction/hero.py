from __future__ import annotations



class Hero:
    @property
    def power_level(self) -> object:
        ...

    @property
    def power_points(self) -> object:
        ...

    @property
    def complications(self) -> object:
        ...

    @property
    def validate_balance(self) -> object:
        ...

    @property
    def enforce_limit_pair(self) -> object:
        ...

    def spend_on(self, trait) -> None:
        ...
