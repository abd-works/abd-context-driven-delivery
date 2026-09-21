"""Scanner: `no-subtype-at-modules` — module-context has no is-a headings."""
from __future__ import annotations

import re
from pathlib import Path

from module_scanner import Module, ModuleScanner

RULE = "no-subtype-at-modules"

_IS_A = re.compile(r"\*is a type of\*", re.IGNORECASE)
_CHILD_PARENT = re.compile(r"^\s*#{1,6}\s+\S.+\s+:\s+\S", re.MULTILINE)


class NoSubtypeAtModulesScanner(ModuleScanner):
    RULE = RULE

    def scan_module(self, root: Path, module: Module) -> list:
        violations: list = []
        try:
            content = module.context_file.read_text(encoding="utf-8")
        except OSError:
            return violations
        for match in _IS_A.finditer(content):
            line = content.count("\n", 0, match.start()) + 1
            violations.append(
                self.violation(
                    f"Module '{module.folder.name}' module-context uses '*is a type of*'. "
                    f"Each concept is its own heading; generalisation waits for model.",
                    location=str(module.context_file),
                    line=line,
                )
            )
        for match in _CHILD_PARENT.finditer(content):
            line = content.count("\n", 0, match.start()) + 1
            violations.append(
                self.violation(
                    f"Module '{module.folder.name}' module-context uses 'Child : Parent'. "
                    f"Generalisation waits for model (`## ChildClass : ClassName`).",
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
            NoSubtypeAtModulesScanner,
            RULE,
            collect_module_files,
        )
    )
