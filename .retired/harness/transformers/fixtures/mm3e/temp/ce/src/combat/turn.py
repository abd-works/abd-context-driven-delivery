from __future__ import annotations



class Turn:
    @property
    def standard_action(self) -> object:
        ...

    @property
    def move_action(self) -> object:
        ...

    @property
    def free_action(self) -> object:
        ...

    @property
    def reaction(self) -> object:
        ...
