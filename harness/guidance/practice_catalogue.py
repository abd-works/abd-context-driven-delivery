"""The one list of CDD practices: each practice's key and the PracticeGuidance class that holds it."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance


class PracticeCatalogue:
    """Every practice CDD ships, in the order the approach walks them: Stories, DDD, UX, Clean Engineering, BDD.

    Callers that only need the practice keys read ``keys()``, which imports no practice code, so the graph and schema
    modules the practices themselves import can use it. Callers that need a practice's fidelities, rules, folder, or
    schema read the shared instance from ``practices()`` or ``practice(key)``; a caller that changes a practice's
    current fidelity or format makes its own with ``create(key)``, so it does not change what other callers see.
    """

    _REFS = {
        "stories": "cdd_guidance.practices.stories.stories:Stories",
        "ddd": "cdd_guidance.practices.ddd.ddd:Ddd",
        "ux": "cdd_guidance.practices.ux.ux:Ux",
        "clean_engineering": "cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering",
        "bdd": "cdd_guidance.practices.bdd.bdd:Bdd",
    }
    _shared: dict[str, PracticeGuidance] = {}

    @classmethod
    def keys(cls) -> tuple[str, ...]:
        """Each practice's key, its folder name under ``cdd_guidance/practices``, such as ``clean_engineering``."""
        return tuple(cls._REFS)

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls._REFS

    @classmethod
    def practices(cls) -> tuple[PracticeGuidance, ...]:
        """The shared instance of every practice. Built once per process: building them takes about 30 ms."""
        return tuple(cls.practice(key) for key in cls._REFS)

    @classmethod
    def practice(cls, key: str) -> PracticeGuidance:
        """The shared instance of the practice ``key``; read it, do not change its current fidelity or format."""
        if key not in cls._shared:
            cls._shared[key] = cls.create(key)
        return cls._shared[key]

    @classmethod
    def create(cls, key: str) -> PracticeGuidance:
        """A new instance of the practice ``key``, for a caller that sets its fidelity, format, or workspace."""
        return cls.practice_class(key)()

    @classmethod
    def practice_class(cls, key: str) -> type[PracticeGuidance]:
        ref = cls._REFS.get(key)
        if ref is None:
            raise KeyError(f"no practice {key!r}; the practices are {', '.join(cls._REFS)}")
        module, name = ref.split(":")
        return getattr(importlib.import_module(module), name)

    @classmethod
    def module_of(cls, key: str) -> str:
        """The Python package that holds the practice ``key``, such as ``cdd_guidance.practices.stories``."""
        return cls._REFS[key].split(":")[0].rsplit(".", 1)[0]

    @classmethod
    def practice_named(cls, slug: str) -> PracticeGuidance | None:
        """The practice whose slug is ``slug``, such as ``clean-engineering``, or that has a fidelity whose slug is
        ``slug``, such as ``stories-story-map``; none when no practice goes by it."""
        for practice in cls.practices():
            if practice.slug == slug or any(fidelity.slug == slug for fidelity in practice.fidelities):
                return practice
        return None

    @classmethod
    def key_of(cls, guidance: PracticeGuidance) -> str | None:
        """The catalogue key of ``guidance``; none for guidance that is not one of the practices, such as a pattern."""
        key = getattr(guidance, "key", None)
        return key if key in cls._REFS else None
