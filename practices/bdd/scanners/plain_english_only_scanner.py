"""Scanner: `plain-english-only` — hierarchy / sketch subject lines stay English.

Rule: plain-english-only

Code syntax in a subject line (`()`, `=>`, `{}`, `[]`, `;`, type annotations)
means implementation leaked into discovery. Sketch call-surface lines that start
with `->` are allowed — those are intentional fidelity detail, not subjects.

Adapted from abd-skills abd-bdd-behavior; targets sketches and describe/it labels
in the context-tool model rather than only `*-hierarchy.txt`.
"""
from __future__ import annotations

import re
from pathlib import Path

from scan import Scanner, ScannerRunner

from bdd_scan_helpers import (
    extract_it_blocks,
    is_sketch_file,
    is_spec_file,
    read_text,
)

RULE = "plain-english-only"

_CODE_SYNTAX = re.compile(r"[()=>{}\[\];]|\.\.\.|:\s*(string|number|boolean|Promise|void)\b")
_SKIP_LINE = re.compile(
    r"^\s*(#|//|/\*|Fidelity:|```|->|HIERARCHY)",
    re.IGNORECASE,
)
_DESCRIBE_LABEL = re.compile(
    r"""(?:description|describe|context)\s*\(\s*['"`](.+?)['"`]""",
    re.IGNORECASE,
)


class PlainEnglishOnlyScanner(Scanner):
    """Flag code syntax in scaffold subjects and describe/it labels."""

    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if is_sketch_file(file_path):
            return self._scan_sketch(file_path)
        if is_spec_file(file_path):
            return self._scan_spec(file_path)
        return []

    def _scan_sketch(self, file_path: Path) -> list:
        content = read_text(file_path)
        if not content:
            return []
        violations = []
        for i, line in enumerate(content.splitlines(), 1):
            if not line.strip() or _SKIP_LINE.search(line):
                continue
            match = _CODE_SYNTAX.search(line)
            if match:
                violations.append(
                    self.violation(
                        f'Code syntax "{match.group(0)}" found in scaffold — '
                        f"hierarchy subjects must be plain English only. "
                        f"Put call-surface detail on a `->` line, not the subject.",
                        location=str(file_path),
                        line=i,
                    )
                )
        return violations

    def _scan_spec(self, file_path: Path) -> list:
        content = read_text(file_path)
        if not content:
            return []
        violations = []
        for i, line in enumerate(content.splitlines(), 1):
            for match in _DESCRIBE_LABEL.finditer(line):
                label = match.group(1)
                code = _CODE_SYNTAX.search(label)
                if code:
                    violations.append(
                        self.violation(
                            f'Describe/context label "{label}" contains code syntax '
                            f'"{code.group(0)}". Subjects must be plain English.',
                            location=str(file_path),
                            line=i,
                        )
                    )
        for lineno, label, _body in extract_it_blocks(file_path, content):
            code = _CODE_SYNTAX.search(label)
            if code:
                violations.append(
                    self.violation(
                        f'Behavior label "{label}" contains code syntax '
                        f'"{code.group(0)}". Observations must be plain English.',
                        location=str(file_path),
                        line=lineno,
                    )
                )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            PlainEnglishOnlyScanner,
            RULE,
            lambda root: sorted(root.rglob("*")),
        )
    )
