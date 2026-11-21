"""The routes by which a class leaves its module other than by being named: registered with one of the framework's
registries, or published as a toolset the installer installs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Optional

from harness.graph.pattern_overlays import REGISTERED_PATTERNS
from harness.guidance.action_catalogue import ACTION_CATALOGUE
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

if TYPE_CHECKING:
    from harness.graph.graph import Node

# The routes a class is public by, in the order a module's public classes are counted by: named by code outside the
# subtree, registered with a framework registry, or published as a toolset.
NAMED = "named"
REGISTERED = "registered"
PUBLISHED = "published"
# What a published class is published as.
_TOOLSET = "toolset"
# The class stereotypes a toolset carries, and those that keep it from being installed on its own: a hosted-only class
# publishes through the class that holds it, and a class not deployed publishes nothing.
_TOOLSET_MARK = "Agent Toolset"
_NOT_PUBLISHED_MARKS = frozenset({"Hosted Only", "No Deploy"})


class RegisteredClasses:
    """<<Value Object>> The classes a package registers with one of the framework's registries when it is imported,
    each by the file that defines it, from the source root, and its name, with the registry's name."""

    def __init__(self, registries: dict[str, Iterable[type]]) -> None:
        self._registry_of = {
            (f"{registered.__module__.replace('.', '/')}.py", registered.__name__): name
            for name, classes in registries.items()
            for registered in classes
        }

    def registry_of(self, node: "Node") -> Optional[str]:
        """The registry that holds the class node defines; none for a class no registry holds."""
        return self._registry_of.get((node.source.file, node.name))


def registered_in_this_process() -> RegisteredClasses:
    """The classes the practices, actions, and patterns this process imported register: ``PRACTICE_CATALOGUE``'s
    practices and supplements, ``ACTION_CATALOGUE``'s toolsets, and ``REGISTERED_PATTERNS``."""
    return RegisteredClasses(
        {
            "PRACTICE_CATALOGUE": (*PRACTICE_CATALOGUE.practice_classes, *PRACTICE_CATALOGUE.supplement_classes),
            "ACTION_CATALOGUE": ACTION_CATALOGUE.toolsets,
            "REGISTERED_PATTERNS": REGISTERED_PATTERNS.classes,
        }
    )


class PublicRoutes:
    """Each route by which a class leaves its module other than by being named: the registry that holds it, and whether
    the installer publishes it as a toolset: a class marked ``@agent_toolset``, or one with an operation published as a
    tool (``@mcp``, ``@agent_tool``), unless it is ``@hosted_only`` or ``@noDeploy``."""

    def __init__(self, registered: RegisteredClasses) -> None:
        self._registered = registered

    def of(self, node: "Node", operations: list["Node"]) -> dict[str, str]:
        """The routes besides naming that make the class node public, each with what it is reached through."""
        routes: dict[str, str] = {}
        registry = self._registered.registry_of(node)
        if registry is not None:
            routes[REGISTERED] = registry
        if self._is_published(node, operations):
            routes[PUBLISHED] = _TOOLSET
        return routes

    def _is_published(self, node: "Node", operations: list["Node"]) -> bool:
        marks = {str(mark) for mark in node.get_fact("stereotypes", []) or []}
        if marks & _NOT_PUBLISHED_MARKS:
            return False
        return _TOOLSET_MARK in marks or any(operation.get_fact("published_as_tool") for operation in operations)
