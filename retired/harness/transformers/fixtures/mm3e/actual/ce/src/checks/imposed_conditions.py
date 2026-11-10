from __future__ import annotations


class ImposedConditions:

    """invariant: same-source supersession removes lesser; different-source parks inactive"""




    @property
    def active_conditions(self) -> object:
        ...


    def apply(self, condition, source) -> None:
        ...


    def supersede(self) -> None:
        ...


    def remove_when_source_ends(self, source) -> None:
        ...
