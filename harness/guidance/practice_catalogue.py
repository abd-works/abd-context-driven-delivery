"""The one list of CDD practices: each practice's key and the PracticeGuidance class that holds it."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar


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
    imported (``register``), as every process that loads the repository's toolsets imports it. The catalogue holds
    classes, never instances: a practice holds the session it works in, its graph, and the formats its fidelities keep,
    so every reader makes the practices it works with and holds them. A session makes a set of its own with
    ``create_all()``, which its graph and its actions share; any other reader, such as the board or a diagnostics probe,
    makes its own set once and keeps it; and a caller that works at a fidelity or format of its own makes one practice
    with ``create(key)``. A practice that extends another holds that practice: one of the same set, or one made with
    it. Making a set reads nothing until a practice's document is first asked for.
    """

    _classes: ClassVar[dict[str, type[PracticeGuidance]]] = {}

    @classmethod
    def register(cls, *practice_classes: type[PracticeGuidance]) -> None:
        """Hold practice_classes as the practices CDD ships, in the order the approach walks them, each by its key."""
        PracticeCatalogue._classes = {practice_class.class_key(): practice_class for practice_class in practice_classes}

    @classmethod
    def keys(cls) -> tuple[str, ...]:
        """Each practice's key, its folder's name, such as ``clean_engineering``."""
        return tuple(cls._registered())

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls._classes

    @classmethod
    def create(cls, key: str, **arguments: object) -> PracticeGuidance:
        """A new instance of the practice ``key``, for a caller that sets its fidelity, format, or workspace outside any
        session; arguments go to the practice's constructor, such as ``fidelity=None`` for a practice at no fidelity. It
        is made with the practices of its set it works with, at no fidelity: the one it extends and its Clean
        Engineering companion, and theirs in turn, so it holds them as a practice of a whole set does."""
        practice = cls.practice_class(key)(**arguments)
        made = {key: practice}
        wanted = list(practice.set_keys)
        while wanted:
            other = wanted.pop()
            if other not in made and cls.has(other):
                made[other] = cls.practice_class(other)(fidelity=None)
                wanted.extend(made[other].set_keys)
        for member in made.values():
            member.hold_set(made)
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
    def _registered(cls) -> dict[str, type[PracticeGuidance]]:
        if not cls._classes:
            raise PracticesNotRegistered()
        return cls._classes
