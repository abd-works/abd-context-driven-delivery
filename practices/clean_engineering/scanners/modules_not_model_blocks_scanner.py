"""Scanner: `modules-not-model-blocks` — no typed compact dumps in module-context."""
from __future__ import annotations

import re
from pathlib import Path

from module_scanner import Module, ModuleScanner

RULE = "modules-not-model-blocks"

_SIX_DASHES = re.compile(r"^------\s*$", re.MULTILINE)
_SOURCES = re.compile(r"^\s*\*\*Sources\s*/\s*context:\*\*", re.MULTILINE | re.IGNORECASE)
_LIVE_INSTANCE = re.compile(r"Live instance:", re.IGNORECASE)


class ModulesNotModelBlocksScanner(ModuleScanner):
    RULE = RULE

    def scan_module(self, root: Path, module: Module) -> list:
        violations: list = []
        try:
            content = module.context_file.read_text(encoding="utf-8")
        except OSError:
            return violations
        for pattern, message in (
            (
                _SIX_DASHES,
                "typed `------` member dump — that waits for model. "
                "Modules stop at Purpose, Seam, Dependencies, Constraint.",
            ),
            (
                _SOURCES,
                "**Sources / context** that lists this folder's own files — "
                "those are the subject, not a source.",
            ),
            (
                _LIVE_INSTANCE,
                "'Live instance:' name inventory with no job. "
                "Say what the caller uses each for, or omit them.",
            ),
        ):
            for match in pattern.finditer(content):
                line = content.count("\n", 0, match.start()) + 1
                violations.append(
                    self.violation(
                        f"Module '{module.folder.name}' module-context has {message}",
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
            ModulesNotModelBlocksScanner,
            RULE,
            collect_module_files,
        )
    )
