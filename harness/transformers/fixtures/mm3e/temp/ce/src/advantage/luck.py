from __future__ import annotations



class Luck:
    @property
    def uses_this_session(self) -> object:
        ...

    @property
    def re_roll(self) -> object:
        ...

    @property
    def refresh(self) -> object:
        ...
