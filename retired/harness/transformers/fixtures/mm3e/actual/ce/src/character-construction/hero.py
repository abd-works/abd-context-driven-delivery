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


    def spend_on(self, trait) -> None:
        ...


    def validate_balance(self) -> None:
        ...


    def enforce_limit_pair(self) -> None:
        ...
