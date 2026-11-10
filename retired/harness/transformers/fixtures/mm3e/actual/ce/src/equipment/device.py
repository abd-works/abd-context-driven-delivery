from __future__ import annotations

from power.power import Power

class Device(Power):




    @property
    def removable(self) -> object:
        ...


    @property
    def easily_removable(self) -> object:
        ...


    @property
    def indestructible(self) -> object:
        ...
