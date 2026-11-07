from __future__ import annotations


class Equipment:




    @property
    def equipment_points(self) -> object:
        ...


    @property
    def items(self) -> object:
        ...


    def pay_for(self, item) -> None:
        ...
