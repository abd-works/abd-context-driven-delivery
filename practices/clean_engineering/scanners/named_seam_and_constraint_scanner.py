"""Scanner: `named-seam-and-constraint` — module-context names Seam and Constraint.

At modules the seam is **Seam (terms)** plus **Constraint**. A Public API
member dump is model — do not require that heading.
"""
from __future__ import annotations

from pathlib import Path

from module_scanner import Module, ModuleScanner

RULE = "named-seam-and-constraint"


class NamedSeamAndConstraintScanner(ModuleScanner):
    RULE = RULE

    def scan_module(self, root: Path, module: Module) -> list:
        violations: list = []
        try:
            content = module.context_file.read_text(encoding="utf-8")
        except OSError:
            return violations
        lowered = content.lower()
        if "seam" not in lowered:
            violations.append(
                self.violation(
                    f"Module '{module.folder.name}' context file does not name a *seam* "
                    f"(the public surface callers depend on).",
                    location=str(module.context_file),
                    line=1,
                )
            )
        if "constraint" not in lowered:
            violations.append(
                self.violation(
                    f"Module '{module.folder.name}' context file does not name a *constraint* "
                    f"(what callers must do or must not do at the seam).",
                    location=str(module.context_file),
                    line=1,
                )
            )
        return violations


if __name__ == "__main__":
    from scan import run_scanner_main
    from module_scanner import collect_module_files

    raise SystemExit(
        run_scanner_main(
            NamedSeamAndConstraintScanner,
            RULE,
            collect_module_files,
        )
    )
