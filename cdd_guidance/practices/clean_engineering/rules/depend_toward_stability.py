"""depend-toward-stability: a module depends on modules at least as many others rely on as rely on itself."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.measures.read_facts import IMPORTED_MODULES_FACT

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class DependTowardStability(PracticeGraphRule):
    """Lists each import of a module by a module that more modules import. How much others rely on a module is counted
    as the modules that import it (``ModuleImports``): a module is a folder that owns a module card, and what a package
    inside it imports is the module's import. An import of anything outside the module, a child module with a card of
    its own among them, is an import of the module that holds it; an import between its own files and packages is none.
    So the rule compares two modules with each other and needs no fixed number.

    The rule requires a judge: some such dependencies are deliberate, such as a module many rely on using a small
    helper that seldom changes, and only a reading tells those from one that should be turned round."""

    slug = "depend-toward-stability"
    node_types = ("Module",)
    requires_judge = True

    def check_practice(self, context: "RuleCheckContext") -> list[Finding]:
        modules = {module.source.file: module for module in context.nodes("Module") if module.source.file}
        importers = self._importers(modules)
        return [
            Finding(module, self._said(module, modules[imported], importers))
            for path, module in modules.items()
            for imported in self._imported(module)
            if imported in modules and imported != path and importers.get(imported, 0) < importers.get(path, 0)
        ]

    def _imported(self, module: "Node") -> list[str]:
        return list(module.get_fact(IMPORTED_MODULES_FACT) or []) if module.has_fact(IMPORTED_MODULES_FACT) else []

    def _importers(self, modules: dict[str, "Node"]) -> dict[str, int]:
        """How many modules import each module."""
        counted: dict[str, set[str]] = {}
        for path, module in modules.items():
            for imported in self._imported(module):
                if imported != path:
                    counted.setdefault(imported, set()).add(path)
        return {imported: len(by) for imported, by in counted.items()}

    def _said(self, module: "Node", imported: "Node", importers: dict[str, int]) -> str:
        relied_on, fewer = importers.get(module.source.file, 0), importers.get(imported.source.file, 0)
        return (
            f"Module '{module.name}', which {self._modules(relied_on)}, imports '{imported.name}', which {self._modules(fewer)}: "
            f"'{module.name}' now changes whenever '{imported.name}' does, and the {relied_on} modules that import it change with it. "
            "Read whether this is deliberate, such as a small helper that seldom changes; "
            f"if it is not, turn the dependency round or move what both need into '{module.name}'."
        )

    def _modules(self, count: int) -> str:
        return f"{count} module imports" if count == 1 else f"{count} modules import"
