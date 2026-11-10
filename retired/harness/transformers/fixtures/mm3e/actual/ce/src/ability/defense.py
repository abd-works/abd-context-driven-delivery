from __future__ import annotations

from checks.trait import Trait

class Defense(Trait):

    """invariant: Toughness cannot be bought above Stamina base"""




    @property
    def source_ability(self) -> object:
        ...


    @property
    def purchased_above_base(self) -> object:
        ...


    def derive_base(self) -> None:
        ...
