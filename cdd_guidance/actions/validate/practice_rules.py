"""The rules a validate of one guidance checks, as its practice and fidelities hold them."""

from __future__ import annotations

from typing import Any

from harness.guidance import Rule


class PracticeRules:
    """The rules of one listed guidance: its shared rules and its fidelities', read from the Rule objects they hold.

    This is the one place validate assembles "the shared rules plus this fidelity's". The practice holds those rules,
    so it is the right owner: these operations belong on PracticeGuidance, where the session board's ticket could
    read them too, instead of assembling them a second time."""

    def __init__(self, guidance: Any) -> None:
        self._guidance = guidance

    def checked_collections(self) -> list:
        """The rule collections a validate checks: the shared rules, then the active fidelity's, else every fidelity's.
        A fidelity that shares its practice's collection is listed once."""
        fidelities = getattr(self._guidance, "fidelities", None)
        current = getattr(fidelities, "current", None)
        chosen = [current] if current is not None else list(fidelities or [])
        collections = [getattr(self._guidance, "rules", None), *(getattr(fidelity, "rules", None) for fidelity in chosen)]
        unique = {id(collection): collection for collection in collections if collection is not None}
        return list(unique.values())

    def checked(self) -> list[Rule]:
        return [rule for collection in self.checked_collections() for rule in collection]

    def every(self) -> list[Rule]:
        """The shared rules and every fidelity's: a saved graph holds the whole practice's hits, so each one's rule text
        is there to show beside it."""
        fidelities = getattr(self._guidance, "fidelities", None) or []
        collections = (getattr(self._guidance, "rules", None), *(fidelity.rules for fidelity in fidelities))
        return [rule for collection in collections if collection is not None for rule in collection]

    def text(self) -> str:
        """The checked collections' rules, as their markdown, for an agent to judge against."""
        texts = (collection.validate.strip() for collection in self.checked_collections())
        return "\n\n".join(text for text in texts if text)
