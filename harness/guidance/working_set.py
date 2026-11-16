"""The practices one practice works with in the set of practices it was made with."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance
    from harness.guidance.practice_supplement import PracticeSupplement


# The practice whose fidelities accompany other practices' fidelities, by its name: a fidelity's ``clean_engineering:``
# setting names the fidelity of this practice whose instructions join its own.
COMPANION_PRACTICE = "clean_engineering"


class WorkingSet:
    """The practices one practice works with, held by reference from the set it was made with: the practice it
    extends (``extended``), the Clean Engineering practice whose fidelities accompany its own (``companion``), and the
    supplements that supplement one of its fidelities (``supplements``). A practice holds one, made with it
    (``practice.working_set``); the catalogue that makes a set hands each practice's working set the set (``hold``), so
    every practice of the set works with the same objects. A practice made apart from any set holds none of them."""

    def __init__(self, practice: PracticeGuidance) -> None:
        self._practice = practice
        self.extended: PracticeGuidance | None = None
        """The practice whose types this practice's schema builds on, which its ``extends`` names, such as the session's
        Clean Engineering for its DDD."""
        self.companion: PracticeGuidance | None = None
        """The Clean Engineering practice whose fidelities accompany this practice's: the one of its set, so a companion
        works in the same session."""
        self.supplements: Sequence[PracticeSupplement] = ()
        """The supplements of the set that supplement one of this practice's fidelities, such as TDD for BDD."""

    @property
    def names(self) -> tuple[str, ...]:
        """The names of the practices this one works with in its set: the one it extends and its Clean Engineering
        companion. The catalogue makes them with it when it makes this practice on its own."""
        own = self._practice.key
        return tuple(name for name in (self._practice.extends, COMPANION_PRACTICE) if name and name != own)

    def hold(self, practices: Mapping[str, PracticeGuidance], supplements: Sequence[PracticeSupplement] = ()) -> None:
        """Hold the practices of the set this practice was made with, by name: the one it extends, and the Clean
        Engineering practice whose fidelities accompany its own; and each of supplements that supplements one of its
        fidelities."""
        if self._practice.extends:
            self.extended = practices[self._practice.extends]
        self.companion = practices.get(COMPANION_PRACTICE)
        self.supplements = [supplement for supplement in supplements if self._practice in supplement.supplemented_practices]
