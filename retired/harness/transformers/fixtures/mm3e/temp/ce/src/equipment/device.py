from __future__ import annotations







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
