"""The classes a package registers with the framework when it is imported, which the framework never imports itself."""

from __future__ import annotations

from typing import Callable, Generic, TypeVar

Registered = TypeVar("Registered")


class ClassRegistry(Generic[Registered]):
    """The classes a package registers when it is imported, in the order it lists them, each by its name. The framework
    names none of them: the practices, the actions, and the patterns each register theirs with the one registry the
    framework keeps for them (``practice_catalogue``, ``action_catalogue``, ``registered_patterns``), an instance held
    once per process because a class is defined once per process, as ``annotation_kinds`` holds the kinds of
    annotation. Registering again holds the classes given in place of those registered before."""

    def __init__(self, name_of: Callable[[type[Registered]], str]) -> None:
        self._name_of = name_of
        self._classes: dict[str, type[Registered]] = {}

    def register(self, *classes: type[Registered]) -> None:
        """Hold classes, in the order listed, each by its name, in place of those registered before."""
        self._classes = {self._name_of(registered): registered for registered in classes}

    @property
    def classes(self) -> tuple[type[Registered], ...]:
        """Each registered class, in the order it was registered."""
        return tuple(self._classes.values())

    @property
    def names(self) -> tuple[str, ...]:
        """Each registered class's name, in the order it was registered."""
        return tuple(self._classes)

    def has(self, name: str) -> bool:
        return name in self._classes

    def named(self, name: str) -> type[Registered] | None:
        """The class registered by name; none when no class goes by it."""
        return self._classes.get(name)
