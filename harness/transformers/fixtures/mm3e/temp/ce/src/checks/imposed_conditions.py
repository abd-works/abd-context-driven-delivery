from __future__ import annotations



class ImposedConditions:
    """invariant: same-source supersession removes lesser; different-source parks inactive"""

    @property
    def supersede(self) -> object:
        ...

    @property
    def remove_when_source_ends(self) -> object:
        ...

    @property
    def active_conditions(self) -> object:
        ...

    def apply(self, condition, source) -> None:
        ...
