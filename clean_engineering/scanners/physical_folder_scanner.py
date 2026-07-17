"""Scanner: `physical-folder` — module context file exists and folder is well-formed.

Checks per module:
- `.context/module-context.md` exists and is non-empty (guaranteed by module discovery)
- Module folder contains at least one Python file
- Module folder is not empty except for its context file

FP profile: LOW. Purely structural.
"""
from __future__ import annotations

from pathlib import Path

from module_scanner import Module, ModuleScanner


class PhysicalFolderScanner(ModuleScanner):

    def scan_module(self, root: Path, module: Module) -> list:
        violations: list = []
        if not module.context_file.is_file() or not module.context_file.read_text(
            encoding="utf-8"
        ).strip():
            violations.append(
                self.violation(
                    f"Module '{module.folder.name}' has an empty or missing "
                    f".context/module-context.md.",
                    location=str(module.context_file),
                    line=1,
                )
            )
            return violations
        if not module.python_files:
            violations.append(
                self.violation(
                    f"Module '{module.folder.name}' has a module-context.md but no "
                    f"Python source files; either add module content or remove the module marker.",
                    location=str(module.folder),
                )
            )
        return violations


if __name__ == "__main__":
    from scanners import run_scanner_main
    from module_scanner import collect_module_files

    raise SystemExit(
        run_scanner_main(PhysicalFolderScanner, "physical-folder", collect_module_files)
    )
