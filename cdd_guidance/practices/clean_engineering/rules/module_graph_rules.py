"""Module / package graph rules — folder facts recorded on Module, Package, and class nodes."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class NamedSeamAndConstraint(PracticeGraphRule):
    slug = "named-seam-and-constraint"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
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

    def check(self, node, context) -> list[str]:
        found = node.get_fact("public_source_internal", "")
        if found == "heading":
            return [f"Module '{node.name}' exposes internal design in a public source file."]
        if found == "mixed":
            return [f"Module '{node.name}' mixes internal design into the public seam."]
        return []


def _python_class_folder(node, context):
    """The folder node a Python class sits in; module-context rules only cover Python sources."""
    if not (node.source.file or "").endswith(".py"):
        return None
    return context.practice.registered(node.get_fact("folder", ""))


class MissingModuleContext(PracticeGraphRule):
    slug = "missing-module-context"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        folder = _python_class_folder(node, context)
        if folder is None or folder.get_fact("has_module_context", True):
            return []
        return [
            f"Module folder '{folder.name}' defines classes but has no .context/module-context.md. "
            "Add one with at minimum: Purpose, Seam, Dependencies."
        ]


class LanguageModulesOneSection(PracticeGraphRule):
    slug = "language-modules-one-section"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
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

    def check(self, node, context) -> list[str]:
        folder = _python_class_folder(node, context)
        if folder is None:
            return []
        return list(folder.get_fact("model_blocks", []))
