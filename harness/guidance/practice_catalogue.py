"""The one list of CDD practices: each practice's key and the PracticeGuidance class that holds it."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from harness.agent_tools.agent_tools import ToolsetReference

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance


class UnknownPractice(KeyError):
    """A practice key the catalogue does not hold, such as a misspelt ``clean-engineering`` for ``clean_engineering``."""

    def __init__(self, key: str, keys: tuple[str, ...]) -> None:
        super().__init__(f"no practice {key!r}; the practices are {', '.join(keys)}")
        self.key = key


class PracticesNotRegistered(LookupError):
    """The practices were asked for in a process where no module that defines them has registered them."""

    def __init__(self) -> None:
        super().__init__("no practices are registered with PracticeCatalogue in this process; import the package that defines them")


class PracticeCatalogue:
    """Every practice CDD ships, in the order the approach walks them: Stories, DDD, UX, Clean Engineering, BDD.

    The framework names no practice. The package that defines the practices registers their classes here when it is
    imported (``register``), as every process that loads the repository's toolsets imports it. Callers that need a
    practice's fidelities, rules, folder, or schema read the catalogue's own instances from ``practices()`` or
    ``practice(key)``. A session makes a set of its own with ``create_all()``, which its graph and its actions share, and
    a caller that works at a fidelity or format of its own outside any session makes its own with ``create(key)``. A
    practice that extends another holds that practice: one of the same set, or one made with it. The catalogue keeps its
    instances because a practice's fidelities and rules are read from its markdown, which does not change while the
    process runs, and every hook and tool call reads them; nothing that reads one sets it.
    """

    _classes: ClassVar[dict[str, type[PracticeGuidance]]] = {}
    _shared: ClassVar[dict[str, PracticeGuidance]] = {}

    @classmethod
    def register(cls, *practice_classes: type[PracticeGuidance]) -> None:
        """Hold practice_classes as the practices CDD ships, in the order the approach walks them, each by its key."""
        PracticeCatalogue._classes = {practice_class.class_key(): practice_class for practice_class in practice_classes}
        PracticeCatalogue._shared = {}

    @classmethod
    def keys(cls) -> tuple[str, ...]:
        """Each practice's key, its folder's name, such as ``clean_engineering``."""
        return tuple(cls._registered())

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls._classes

    @classmethod
    def holds(cls, practice_class: type) -> bool:
        """Whether practice_class is one of the practices CDD ships, rather than a pattern or a practice of a project."""
        return practice_class in cls._classes.values()

    @classmethod
    def practices(cls) -> tuple[PracticeGuidance, ...]:
        """The shared instance of every practice. Built once per process: building them takes about 30 ms."""
        if len(cls._shared) < len(cls._registered()):
            PracticeCatalogue._shared = {practice.key: practice for practice in cls.create_all()}
        return tuple(cls._shared.values())

    @classmethod
    def practice(cls, key: str) -> PracticeGuidance:
        """The shared instance of the practice ``key``; read it, do not change its current fidelity or format."""
        cls.practice_class(key)
        cls.practices()
        return cls._shared[key]

    @classmethod
    def create(cls, key: str, **arguments: object) -> PracticeGuidance:
        """A new instance of the practice ``key``, for a caller that sets its fidelity, format, or workspace outside any
        session; arguments go to the practice's constructor, such as ``fidelity=None`` for a practice at no fidelity. A
        practice that extends another holds a new instance of that one, made with it."""
        practice = cls.practice_class(key)(**arguments)
        if practice.extends:
            practice.extended = cls.create(practice.extends, fidelity=None)
        return practice

    @classmethod
    def create_all(cls, **arguments: object) -> list[PracticeGuidance]:
        """A new instance of every practice, in catalogue order, made with arguments, such as ``fidelity=None``; each
        holds the others of the same set it works with, such as the practice it extends. A session makes its practices
        this way, so its graph and its actions work with the same objects."""
        made = {key: practice_class(**arguments) for key, practice_class in cls._registered().items()}
        for practice in made.values():
            practice.hold_set(made)
        return list(made.values())

    @classmethod
    def practice_class(cls, key: str) -> type[PracticeGuidance]:
        practice_class = cls._registered().get(key)
        if practice_class is None:
            raise UnknownPractice(key, cls.keys())
        return practice_class

    @classmethod
    def key_of(cls, toolset_ref: str) -> str | None:
        """The key of the practice whose toolset ref is toolset_ref, such as ``stories`` for its ``module:Class``; none
        for a ref that is no practice CDD has."""
        return next((key for key, ref in cls._refs().items() if ref == toolset_ref), None)

    @classmethod
    def practice_named(cls, slug: str) -> PracticeGuidance | None:
        """The practice whose slug is ``slug``, such as ``clean-engineering``, or that has a fidelity whose slug is
        ``slug``, such as ``stories-story-map``; none when no practice goes by it."""
        for practice in cls.practices():
            if practice.slug == slug or any(fidelity.slug == slug for fidelity in practice.fidelities):
                return practice
        return None

    @classmethod
    def toolset_ref(cls, slug: str) -> str | dict[str, str] | None:
        """The toolset ref a guidance action lists for slug: the practice's ``module:Class`` for a practice's slug, such
        as ``stories``; that ref with the fidelity's name for a fidelity's slug, such as ``stories-story-map``, or for a
        fidelity's bare name, such as ``story_map`` or ``story-map``. A bare name two practices share, such as
        ``model``, is the first practice's in catalogue order. None when no practice goes by slug."""
        refs = cls._refs()
        for practice in cls.practices():
            if practice.slug == slug:
                return refs[practice.key]
            fidelity = next((fidelity for fidelity in practice.fidelities if fidelity.slug == slug), None)
            if fidelity is not None:
                return {"toolset": refs[practice.key], "fidelity": fidelity.name}
        return cls._bare_fidelity_ref(slug)

    @classmethod
    def _bare_fidelity_ref(cls, name: str) -> dict[str, str] | None:
        refs = cls._refs()
        for practice in cls.practices():
            for fidelity in practice.fidelities:
                if name in (fidelity.name, fidelity.name.replace("_", "-")):
                    return {"toolset": refs[practice.key], "fidelity": fidelity.name}
        return None

    @classmethod
    def _refs(cls) -> dict[str, str]:
        return {key: str(ToolsetReference.of(practice_class)) for key, practice_class in cls._registered().items()}

    @classmethod
    def _registered(cls) -> dict[str, type[PracticeGuidance]]:
        if not cls._classes:
            raise PracticesNotRegistered()
        return cls._classes
