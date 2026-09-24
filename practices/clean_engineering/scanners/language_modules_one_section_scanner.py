"""Scanner: `language-modules-one-section` — no `## Language` / `## Modules` wrappers."""
from __future__ import annotations

import re
from pathlib import Path

from module_scanner import Module, ModuleScanner

RULE = "language-modules-one-section"

_WRAPPER_HEADING = re.compile(
    r"^\s*#{1,6}\s+(Language|Modules)\b",
    re.MULTILINE | re.IGNORECASE,
)


class LanguageModulesOneSectionScanner(ModuleScanner):
    RULE = RULE

    def scan_module(self, root: Path, module: Module) -> list:
        violations: list = []
        try:
            content = module.context_file.read_text(encoding="utf-8")
        except OSError:
            return violations
        for match in _WRAPPER_HEADING.finditer(content):
            line = content.count("\n", 0, match.start()) + 1
            heading = match.group(1)
            violations.append(
                self.violation(
                    f"Module '{module.folder.name}' module-context has a '{heading}' heading. "
                    f"Put language at the top of each # path; drop ## Language and ## Modules.",
                    location=str(module.context_file),
                    line=line,
                )
            )
        return violations


if __name__ == "__main__":
    from scan import run_scanner_main
    from module_scanner import collect_module_files

    raise SystemExit(
        run_scanner_main(
            LanguageModulesOneSectionScanner,
            RULE,
            collect_module_files,
        )
    )
