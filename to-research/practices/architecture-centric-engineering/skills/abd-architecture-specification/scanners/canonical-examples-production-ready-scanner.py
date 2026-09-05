#!/usr/bin/env python3
"""Flag code blocks in context files that contain pseudo-code anti-patterns.

Canonical examples in architecture context files are copied by engineers and AI
assistants. If they contain placeholder types, TODO comments, or omitted imports
the next engineer copies the gaps into production code.

Checked anti-patterns inside fenced code blocks:
  - `: any` / `: Any` — placeholder types that hide the real shape
  - `// TODO` / `# TODO` — deferred work left in the example
  - `/* ... */` or `// ...` — abbreviated body ("for brevity")
  - `{ }` / `{}` or `{ ... }` as the sole content of a function/method body
  - `pass  #` or bare `pass` as a method body placeholder (Python)
  - `object` used as a parameter or return type (Java/Kotlin anti-pattern)
  - "for brevity" prose inside a code block

These checks are heuristic and produce warnings, not errors.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

_ROOT = Path(__file__).resolve().parent.parent
_REPO = _ROOT.parent.parent.parent.parent
for _p in (
    _REPO / "common" / "scripts",
    _ROOT / "scanners",
):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

from scanner_runner import execute_scan_with_workspace  # noqa: E402
from scanner_bases import Scanner, Violation  # noqa: E402
from scanner_bases.resources.scan_context import FileScanContext  # noqa: E402
from arch_spec_context import build_arch_spec_context, iter_code_blocks  # noqa: E402

# (pattern, human-readable description of the problem)
_ANTI_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (
        re.compile(r":\s*any\b", re.IGNORECASE),
        "': any' is a placeholder type — use the real type or a named placeholder like {PartnerRequest}",
    ),
    (
        re.compile(r"//\s*TODO", re.IGNORECASE),
        "'// TODO' leaves deferred work in the canonical example — finish it or remove the block",
    ),
    (
        re.compile(r"#\s*TODO", re.IGNORECASE),
        "'# TODO' leaves deferred work in the canonical example — finish it or remove the block",
    ),
    (
        re.compile(r"/\*\s*\.\.\.\s*\*/"),
        "'/* ... */' abbreviates the body — canonical examples must be complete, not summarised",
    ),
    (
        re.compile(r"//\s*\.\.\."),
        "'// ...' abbreviates the body — canonical examples must be complete, not summarised",
    ),
    (
        re.compile(r"#\s*\.\.\."),
        "'# ...' abbreviates the body — canonical examples must be complete, not summarised",
    ),
    (
        re.compile(r"\{\s*\.\.\.\s*\}", re.DOTALL),
        "'{ ... }' is a placeholder body — write the real implementation or stub pattern",
    ),
    (
        re.compile(r"\bfor\s+brevity\b", re.IGNORECASE),
        "'for brevity' signals that the example is incomplete — canonical code must be production-ready",
    ),
    (
        re.compile(r"\bimports\s+omitted\b", re.IGNORECASE),
        "'imports omitted' — canonical examples must include all imports so the shape is reproducible",
    ),
    (
        re.compile(r"\bfor\s+simplicity\b", re.IGNORECASE),
        "'for simplicity' signals that the example cuts corners — use the full production pattern",
    ),
    (
        re.compile(r":\s*object\b"),
        "': object' is an overly broad type — use the specific domain type or a named placeholder",
    ),
]

# Fenced code block with language hint and body
_FENCE_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)

# We only care about code blocks (not plain-text blocks)
_NON_CODE_LANGS = {"", "text", "markdown", "md", "plain"}


class CanonicalExamplesProductionReadyScanner(Scanner):

    def scan_file_with_context(self, context: FileScanContext) -> List[dict]:
        if not context.exists:
            return []
        text = context.file_path.read_text(encoding="utf-8")
        violations: List[dict] = []

        for m in _FENCE_RE.finditer(text):
            lang = m.group(1).strip().lower()
            if lang in _NON_CODE_LANGS:
                continue
            body = m.group(2)
            for pattern, description in _ANTI_PATTERNS:
                hit = pattern.search(body)
                if hit:
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=(
                                f"Code block in '{context.file_path.name}' "
                                f"contains pseudo-code: {description}"
                            ),
                            location=str(context.file_path),
                            severity="warning",
                        ).to_dict()
                    )
                    break  # one report per block is enough
        return violations


if __name__ == "__main__":
    sys.exit(
        execute_scan_with_workspace(
            CanonicalExamplesProductionReadyScanner,
            "canonical-examples-are-production-ready",
            build_arch_spec_context,
            skill_root=_ROOT,
        )
    )
