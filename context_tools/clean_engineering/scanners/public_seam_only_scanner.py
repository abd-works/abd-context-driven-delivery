"""Scanner: `public-seam-only` — module-context.md stays use / extend / dependencies.

Flags `.context/module-context.md` content that leaks internals:

- Forbidden headings (Internal design, Participants, Pickup, Tests, …)
- Underscore-prefixed private names (`_CliAgentLog`, `_await_pickup`, …)
  except public authoring markers `_is_*`

FP profile: LOW. Vocabulary and naming conventions are deliberate.
"""
from __future__ import annotations

import re
from pathlib import Path

from module_scanner import Module, ModuleScanner

RULE = "public-seam-only"

_FORBIDDEN_HEADINGS = frozenset(
    {
        "internal design",
        "internal",
        "internals",
        "participants",
        "domain separation",
        "pickup",
        "layout",
        "known scan notes",
        "implementation",
        "implementation notes",
        "scan violations",
        "tests",
        "scanners",
        "modules fidelity",
    }
)

_HEADING = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")
# Private types/helpers/methods: leading underscore, not the public `_is_*` markers.
# Leading-underscore private names. Skip `*_scanner.py` globs and `_is_*` markers.
_PRIVATE_NAME = re.compile(
    r"(?<![A-Za-z0-9*])(_(?!is_)[A-Za-z][A-Za-z0-9_]*)\b"
)


class PublicSeamOnlyScanner(ModuleScanner):
    RULE = RULE

    def scan_module(self, root: Path, module: Module) -> list:
        violations: list = []
        context_file = module.context_file
        if not context_file.is_file():
            return violations
        try:
            content = context_file.read_text(encoding="utf-8")
        except OSError:
            return violations

        for lineno, line in enumerate(content.splitlines(), start=1):
            match = _HEADING.match(line)
            if not match:
                continue
            heading = match.group(1).strip()
            key = heading.lower()
            if key in _FORBIDDEN_HEADINGS or "internal" in key:
                violations.append(
                    self.violation(
                        f"Module '{module.folder.name}' module-context heading "
                        f"'{heading}' is not part of the public seam "
                        f"(use / extend / dependencies only). "
                        f"Drop internals; keep Purpose, Seam, Public API, "
                        f"Constraint, Extend, Dependencies.",
                        location=str(context_file),
                        line=lineno,
                    )
                )

        for match in _PRIVATE_NAME.finditer(content):
            name = match.group(1)
            line = content.count("\n", 0, match.start()) + 1
            violations.append(
                self.violation(
                    f"Module '{module.folder.name}' module-context names private "
                    f"'{name}'. Underscore-prefixed types/helpers stay out of "
                    f"module-context (except public `_is_*` authoring markers).",
                    location=str(context_file),
                    line=line,
                )
            )
        return violations


if __name__ == "__main__":
    from scan import run_scanner_main
    from module_scanner import collect_module_files

    raise SystemExit(
        run_scanner_main(
            PublicSeamOnlyScanner,
            RULE,
            collect_module_files,
        )
    )
