"""Scanner: `low-coupling` — module depends on few external modules.

Counts distinct *sibling* modules (other module folders under the same parent)
that this module imports from. Flags modules whose fan-out exceeds a threshold.

Only sibling-module imports are counted; standard library and third-party
imports are ignored. This keeps the metric focused on architectural coupling.

FP profile: MEDIUM. Threshold-based. A module with genuinely broad coordination
responsibility (e.g. a top-level composition root) can legitimately import from
many siblings — this scanner's report should be treated as an indicator for
human review, not an absolute failure.
"""
from __future__ import annotations

import ast
from pathlib import Path

from module_scanner import Module, ModuleScanner

MAX_SIBLING_IMPORTS = 8


class LowCouplingScanner(ModuleScanner):

    def scan_module(self, root: Path, module: Module) -> list:
        sibling_names = _sibling_module_names(module.folder)
        if not sibling_names:
            return []
        imported: set[str] = set()
        for file_path in module.python_files:
            tree = self.parse_python(file_path)
            if tree is None:
                continue
            for node in ast.walk(tree):
                imported.update(_imported_sibling_names(node, sibling_names))
        if len(imported) <= MAX_SIBLING_IMPORTS:
            return []
        return [
            self.violation(
                f"Module '{module.folder.name}' imports from {len(imported)} sibling "
                f"modules ({', '.join(sorted(imported))}). Fan-out above "
                f"{MAX_SIBLING_IMPORTS} suggests high coupling — introduce a facade or "
                f"push shared logic behind a mediator.",
                location=str(module.folder),
            )
        ]


def _sibling_module_names(module_folder: Path) -> set[str]:
    parent = module_folder.parent
    if not parent.is_dir():
        return set()
    names: set[str] = set()
    for sibling in parent.iterdir():
        if sibling == module_folder or not sibling.is_dir():
            continue
        if (sibling / ".context" / "module-context.md").is_file():
            names.add(sibling.name)
    return names


def _imported_sibling_names(node: ast.AST, sibling_names: set[str]) -> set[str]:
    found: set[str] = set()
    if isinstance(node, ast.Import):
        for alias in node.names:
            root_name = alias.name.split(".")[0]
            if root_name in sibling_names:
                found.add(root_name)
    elif isinstance(node, ast.ImportFrom):
        module_ref = node.module or ""
        root_name = module_ref.split(".")[0]
        if root_name in sibling_names:
            found.add(root_name)
    return found


if __name__ == "__main__":
    from scanners import run_scanner_main
    from module_scanner import collect_module_files

    raise SystemExit(
        run_scanner_main(LowCouplingScanner, "low-coupling", collect_module_files)
    )
