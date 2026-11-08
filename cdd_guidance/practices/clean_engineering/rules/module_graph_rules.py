"""Module / package graph rules — folder facts recorded on Module, Package, and class nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class NamedSeamAndConstraint(PracticeGraphRule):
    slug = "named-seam-and-constraint"
    node_types = ("Module",)

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if not node.has_fact("has_module_context"):
            return []
        if node.get_fact("has_module_context") or node.get_fact("has_bounded_context"):
            return []
        return [
            f"Module '{node.name}' is missing .context/module-context.md "
            "or .context/bounded-context.md."
        ]


class PublicSeamOnly(PracticeGraphRule):
    slug = "public-seam-only"
    node_types = ("Module", "Package")

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        found = node.get_fact("public_source_internal", "")
        if found == "heading":
            return [f"Module '{node.name}' exposes internal design in a public source file."]
        if found == "mixed":
            return [f"Module '{node.name}' mixes internal design into the public seam."]
        return []


def _python_class_folder(node: "Node", context: "RuleCheckContext") -> "Node | None":
    """The folder node a Python class sits in; module-context rules only cover Python sources."""
    if not (node.source.file or "").endswith(".py"):
        return None
    return next(iter(context.targets(node, "belongsTo")), None)


class MissingModuleContext(PracticeGraphRule):
    """A folder of classes needs a module card: its own, or one on a folder above it inside the project, because a
    nested folder without a card rolls up to the nearest enclosing module (`deep-module`). The project's own root card
    lists the modules; it is not a module's card."""

    slug = "missing-module-context"
    node_types = ("OoadClass",)

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        folder = _python_class_folder(node, context)
        if folder is None or folder.get_fact("has_module_context", True):
            return []
        if self._enclosing_card(folder, context):
            return []
        return [
            f"Module folder '{folder.name}' defines classes but has no .context/module-context.md. "
            "Add one with at minimum: Purpose, Seam, Dependencies."
        ]


    def _enclosing_card(self, folder: "Node", context: "RuleCheckContext") -> bool:
        """True when a folder that owns this one, short of the project's root, holds a module card."""
        parent = context.graph.direct_parent(folder)
        while parent is not None and parent.type in ("Module", "Package"):
            if parent.get_fact("has_module_context"):
                return True
            parent = context.graph.direct_parent(parent)
        return False


class LanguageModulesOneSection(PracticeGraphRule):
    slug = "language-modules-one-section"
    node_types = ("OoadClass",)

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        folder = _python_class_folder(node, context)
        if folder is None or not folder.get_fact("modules_heading"):
            return []
        return [
            f"Module '{folder.name}' module-context has a 'Modules' heading. Language is the opening "
            "lines of each # path card — drop ## Modules and do not add ## Language."
        ]


class ModulesNotModelBlocks(PracticeGraphRule):
    slug = "modules-not-model-blocks"
    node_types = ("OoadClass",)

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        folder = _python_class_folder(node, context)
        if folder is None:
            return []
        return list(folder.get_fact("model_blocks", []))
