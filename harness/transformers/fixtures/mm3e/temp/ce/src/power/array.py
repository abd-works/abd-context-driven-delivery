from __future__ import annotations



class Array:
    """invariant: non-dynamic array effects are mutually exclusive"""

    @property
    def base_effect(self) -> object:
        ...

    @property
    def alternates(self) -> object:
        ...

    @property
    def dynamic(self) -> object:
        ...

    @property
    def switch_active(self) -> object:
        ...

    @property
    def reallocate(self) -> object:
        ...
