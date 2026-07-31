"""Scanner: `named-seam-and-constraint` - module-context.md declares seam and constraint.

The Seam section should be natural-language prose (not labeled sub-slots). This
scanner only checks that the ideas are named in the file (case-insensitive):
- The word "seam" appears (public surface callers depend on)
- The word "constraint" appears (what callers must / must not do)
- A public API section is present (heading like `## Public API` or `## Public surface`)

FP profile: LOW. Textual presence of well-defined vocabulary.
"""
from __future__ import annotations

import re
from pathlib import Path

from module_scanner import Module, ModuleScanner

_HEADING_PATTERN = re.compile(
    r"^\s*#{1,6}\s+(public\s+api|public\s+surface)\b",
    re.IGNORECASE | re.MULTILINE,
)


class NamedSeamAndConstraintScanner(ModuleScanner):

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
        if not _HEADING_PATTERN.search(content):
            violations.append(
                self.violation(
                    f"Module '{module.folder.name}' context file lacks a 'Public API' or "
                    f"'Public surface' heading listing the seam's classes and operations.",
                    location=str(module.context_file),
                    line=1,
                )
            )
        return violations


if __name__ == "__main__":
    from scanners import run_scanner_main
    from module_scanner import collect_module_files

    raise SystemExit(
        run_scanner_main(
            NamedSeamAndConstraintScanner,
            "named-seam-and-constraint",
            collect_module_files,
        )
    )
