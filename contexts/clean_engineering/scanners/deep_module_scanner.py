"""Scanner: `deep-module` — small public seam, substantial functionality behind it.

Heuristic: count public top-level symbols (classes and functions whose names do
not begin with underscore) across all module files, and count total top-level
symbols. Flag when the public-to-total ratio exceeds a threshold — the module
exports too much of its internals for the seam to be meaningful.

Threshold rationale: Ousterhout's deep modules (A Philosophy of Software Design)
ask for a *small* interface relative to hidden functionality (iceberg / tall-narrow
rectangle) — not a numeric %. Secondary heuristics often cite few public methods
(e.g. ~3–7) and implementation much larger than the interface. A 70% public-symbol
cap still allows a mostly-exported module and is too loose for that intent. Cap at
40% so a clear majority of top-level symbols stay private. Empirically, Java
codebases also show substantial over-exposure (~20–25% of classes/methods more
visible than needed), which argues against a high public-ratio allowance.

FP profile: LOW-MEDIUM. Threshold-based heuristic. Very small modules are
skipped (no meaningful ratio) to reduce false positives.
"""
from __future__ import annotations

import ast
from pathlib import Path

from module_scanner import Module, ModuleScanner

MIN_SYMBOLS_TO_JUDGE = 5
MAX_PUBLIC_RATIO = 0.40


class DeepModuleScanner(ModuleScanner):

    def scan_module(self, root: Path, module: Module) -> list:
        total = 0
        public = 0
        for file_path in module.python_files:
            tree = self.parse_python(file_path)
            if tree is None:
                continue
            for node in tree.body:
                if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                total += 1
                if not node.name.startswith("_"):
                    public += 1
        if total < MIN_SYMBOLS_TO_JUDGE:
            return []
        ratio = public / total
        if ratio > MAX_PUBLIC_RATIO:
            percent_public = int(round(ratio * 100))
            return [
                self.violation(
                    f"Module '{module.folder.name}' exposes {public} of {total} top-level "
                    f"symbols publicly ({percent_public}%). A deep module keeps a short "
                    f"named seam; push internals private (leading underscore) or split the module.",
                    location=str(module.folder),
                )
            ]
        return []


if __name__ == "__main__":
    from scanners import run_scanner_main
    from module_scanner import collect_module_files

    raise SystemExit(
        run_scanner_main(DeepModuleScanner, "deep-module", collect_module_files)
    )
