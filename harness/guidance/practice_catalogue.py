"""The one list of CDD practices: each practice's name and the PracticeGuidance class that holds it, and the set of
practices one reader makes from it."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, overload

from harness.annotations.class_folder import class_folder
from harness.annotations.class_registry import ClassRegistry


if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance


class UnknownPractice(KeyError):
    """A practice name the catalogue does not hold, such as a misspelt ``clean-engineering`` for ``clean_engineering``."""

    def __init__(self, name: str, names: tuple[str, ...]) -> None:
        super().__init__(f"no practice {name!r}; the practices are {', '.join(names)}")
        self.name = name


class PracticesNotRegistered(LookupError):
    """The practices were asked for in a process where no module that defines them has registered them."""

    def __init__(self) -> None:
        super().__init__("no practices are registered with PRACTICE_CATALOGUE in this process; import the package that defines them")


class PracticeSet(Sequence["PracticeGuidance"]):
    """One set of practices a reader made and holds, in catalogue order, each holding the others of the set it works
    with. The set answers which of its practices or fidelities a slug a person types names, so every reader that reads
    a slug asks its own set once rather than searching the practices itself."""

    def __init__(self, practices: Iterable[PracticeGuidance]) -> None:
        self._practices = tuple(practices)

    @overload
    def __getitem__(self, index: int) -> PracticeGuidance: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[PracticeGuidance]: ...

    def __getitem__(self, index: int | slice) -> PracticeGuidance | Sequence[PracticeGuidance]:
        return self._practices[index]

    def __len__(self) -> int:
        return len(self._practices)

    def answering(self, slug: str) -> PracticeGuidance | FidelityGuidance | None:
        """The practice or fidelity of this set whose slug slug is, such as ``stories`` or ``stories-story-map``; none
        for a slug no practice of the set goes by."""
        return next((found for practice in self._practices if (found := practice.answers_to(slug)) is not None), None)

    def practice_answering(self, slug: str) -> PracticeGuidance | None:
        """The practice of this set that slug names, by its own slug or one of its fidelities'; none for a slug no
        practice of the set goes by."""
        return next((practice for practice in self._practices if practice.answers_to(slug) is not None), None)

    def named(self, slug: str) -> PracticeGuidance | FidelityGuidance | None:
        """The practice or fidelity slug names: by its slug (``answering``), else a fidelity by its bare name in kebab
        or snake case, such as ``story-map``, the first practice's in catalogue order when two share it."""
        found = self.answering(slug)
        if found is not None:
            return found
        return next((fidelity for practice in self._practices if (fidelity := practice.fidelities.called(slug)) is not None), None)

    @property
    def slugs(self) -> list[str]:
        """Every slug a person can name one of the set by: each practice's, then each of its fidelities'."""
        return [slug for practice in self._practices for slug in (practice.slug, *practice.fidelity_slugs)]


class PracticeCatalogue:
    """Every practice CDD ships, in the order the approach walks them: Stories, DDD, UX, Clean Engineering, BDD.

    The framework names no practice. The package that defines the practices registers their classes with the process's
    one catalogue (``PRACTICE_CATALOGUE.register``) when it is imported, as every process that loads the repository's
    toolsets imports it. The catalogue holds classes, never instances: a practice holds the session it works in, its
    graph, and the formats its fidelities keep, so every reader makes the practices it works with and holds them. A
    session makes a set of its own with ``create_all()``, which its graph and its actions share; any other reader, such
    as the board or a diagnostics probe, makes its own set once and keeps it; and a caller that works at a fidelity or
    format of its own makes one practice with ``create(name)``. A practice that extends another holds that practice: one
    of the same set, or one made with it. Making a set reads nothing until a practice's document is first asked for.
    """

    def __init__(self) -> None:
        self._practices: ClassRegistry[PracticeGuidance] = ClassRegistry(self._name_of)
        self._supplements: ClassRegistry[PracticeGuidance] = ClassRegistry(self._name_of)

    def _name_of(self, practice_class: type[PracticeGuidance]) -> str:
        """A practice's name, its folder's name, such as ``clean_engineering``."""
        return class_folder(practice_class).name

    def register(self, *practice_classes: type[PracticeGuidance]) -> None:
        """Hold practice_classes as the practices CDD ships, in the order the approach walks them, each by its name."""
        self._practices.register(*practice_classes)

    def register_supplements(self, *supplement_classes: type[PracticeGuidance]) -> None:
        """Hold supplement_classes as the practice supplements CDD ships, apart from the practices, so ``names`` and the
        board never list one; registering none clears them."""
        self._supplements.register(*supplement_classes)

    @property
    def supplement_classes(self) -> tuple[type[PracticeGuidance], ...]:
        """The practice supplements registered, in the order they were registered."""
        return self._supplements.classes

    @property
    def names(self) -> tuple[str, ...]:
        """Each practice's name, its folder's name, such as ``clean_engineering``."""
        return self._registered().names

    @property
    def practice_classes(self) -> tuple[type[PracticeGuidance], ...]:
        """Each practice's class, in the order the approach walks them."""
        return self._registered().classes

    def has(self, name: str) -> bool:
        return self._practices.has(name)

    def create(self, name: str, **arguments: object) -> PracticeGuidance:
        """A new instance of the practice called name, for a caller that sets its fidelity, format, or workspace outside
        any session; arguments go to the practice's constructor, such as ``fidelity=None`` for a practice at no
        fidelity. It is made with the practices of its set it works with, at no fidelity: the one it extends and its
        Clean Engineering companion, and theirs in turn, so it holds them as a practice of a whole set does."""
        practice = self.practice_class(name)(**arguments)
        made = {name: practice}
        wanted = list(practice.working_set.names)
        while wanted:
            other = wanted.pop()
            if other not in made and self.has(other):
                made[other] = self.practice_class(other)(fidelity=None)
                wanted.extend(made[other].working_set.names)
        for member in made.values():
            member.working_set.hold(made)
        return practice

    def create_all(self, **arguments: object) -> PracticeSet:
        """A new instance of every practice, in catalogue order, made with arguments, such as ``fidelity=None``; each
        holds the others of the same set it works with, such as the practice it extends. A session makes its practices
        this way, so its graph and its actions work with the same objects."""
        made = {name: practice_class(**arguments) for name, practice_class in zip(self.names, self.practice_classes)}
        supplements = self._always_on_supplements(made)
        for practice in made.values():
            practice.working_set.hold(made, supplements)
        return PracticeSet(made.values())

    def _always_on_supplements(self, made: dict[str, PracticeGuidance]) -> list[PracticeGuidance]:
        """One of each registered supplement that is on in every session, each holding the set's own fidelities it
        supplements."""
        supplements = [supplement_class() for supplement_class in self._supplements.classes]
        for supplement in supplements:
            supplement.working_set.hold(made)
        return [supplement for supplement in supplements if supplement.always_apply]

    def practice_class(self, name: str) -> type[PracticeGuidance]:
        practice_class = self._registered().named(name)
        if practice_class is None:
            raise UnknownPractice(name, self.names)
        return practice_class

    def _registered(self) -> ClassRegistry[PracticeGuidance]:
        if not self._practices.names:
            raise PracticesNotRegistered()
        return self._practices


# The practices are classes, and a class is defined once per process, so the catalogue of them is one per process too.
PRACTICE_CATALOGUE = PracticeCatalogue()
