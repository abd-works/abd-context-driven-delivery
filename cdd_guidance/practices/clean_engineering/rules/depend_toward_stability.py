"""depend-toward-stability: a module depends on modules at least as many others rely on as rely on itself."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.reading.folder_facts import ModuleImports, is_under

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class DependTowardStability(PracticeGraphRule):
    """Lists each import of a module by a module that more modules import. How much others rely on a module is counted
    as the modules that import it (``ModuleImports``): a module is a folder that owns a module card, and what a package
    inside it imports is the module's import, so the rule compares two modules with each other and needs no fixed
    number. A module nested beneath the importing module, or above it, is its own part and is not compared.

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
            if imported in modules and self._another_module(path, imported) and importers.get(imported, 0) < importers.get(path, 0)
        ]

    def _imported(self, module: "Node") -> list[str]:
        return list(module.get_fact(ModuleImports.IMPORTED) or []) if module.has_fact(ModuleImports.IMPORTED) else []

    def _importers(self, modules: dict[str, "Node"]) -> dict[str, int]:
        """How many modules import each module, itself and the modules nested in it or holding it aside."""
        counted: dict[str, set[str]] = {}
        for path, module in modules.items():
            for imported in self._imported(module):
                if self._another_module(path, imported):
                    counted.setdefault(imported, set()).add(path)
        return {imported: len(by) for imported, by in counted.items()}

    def _another_module(self, own: str, other: str) -> bool:
        """True when other is neither own itself nor a module beneath or above it."""
        return other != own and not is_under(other, own) and not is_under(own, other)

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
