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


    def switch_active(self) -> None:
        ...


    def reallocate(self) -> None:
        ...
