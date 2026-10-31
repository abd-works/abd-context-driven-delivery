from __future__ import annotations







class Defense(Trait):
    """invariant: Toughness cannot be bought above Stamina base"""

    @property
    def source_ability(self) -> object:
        ...

    @property
    def purchased_above_base(self) -> object:
        ...

    @property
    def derive_base(self) -> object:
        ...
