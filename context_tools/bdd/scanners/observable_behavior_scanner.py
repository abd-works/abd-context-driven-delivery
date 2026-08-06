"""Scanner: `observable-behavior` — assert public outcomes, never private state.

Rule: observable-behavior

Tests prove what a stakeholder can verify without reading production code.
Private-field access (`._field`), private method calls, and expects on
underscore members are violations.

Adapted from abd-skills abd-bdd-development (JS-only) for Python expects and
Jest/JS assertions.
"""
from __future__ import annotations

import re
from pathlib import Path

from scanners import Scanner, ScannerRunner

from bdd_scan_helpers import is_spec_file, read_text

RULE = "observable-behavior"

_EXPECT_PRIVATE = re.compile(
    r"(?:expect\s*\([^)]*\._\w+|expect\([^)]*\)\.to\([^)]*\._\w+)"
)
_DIRECT_PRIVATE = re.compile(
    r"(?:result|output|instance|obj|subject|sut|actual|entity|self\.\w+)\s*\.\s*_\w+"
)
_PRIVATE_METHOD_CALL = re.compile(
    r"(?:result|output|instance|obj|subject|sut|entity)\s*\.\s*_\w+\s*\("
)
_PYTHON_EXPECT_PRIVATE = re.compile(r"expect\([^)]*\._\w+")


class ObservableBehaviorScanner(Scanner):
    """Flag assertions and probes that reach private members."""

    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if not is_spec_file(file_path):
            return []
        content = read_text(file_path)
        if not content:
            return []

        violations = []
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "//")):
                continue

            if _EXPECT_PRIVATE.search(stripped) or _PYTHON_EXPECT_PRIVATE.search(stripped):
                field = re.search(r"\._(\w+)", stripped)
                name = field.group(1) if field else "private field"
                violations.append(
                    self.violation(
                        f'Assertion accesses private field "_{name}". '
                        f"Assert observable behavior through the public API.",
                        location=str(file_path),
                        line=i,
                        severity="warning",
                    )
                )
                continue

            if _PRIVATE_METHOD_CALL.search(stripped):
                method = re.search(r"\.(_\w+)\s*\(", stripped)
                name = method.group(1) if method else "_method"
                violations.append(
                    self.violation(
                        f'Test calls private method "{name}". '
                        f"Test through the public interface to verify observable behavior.",
                        location=str(file_path),
                        line=i,
                        severity="warning",
                    )
                )
                continue

            if _DIRECT_PRIVATE.search(stripped) and "expect" not in stripped:
                field = re.search(r"\.(_\w+)", stripped)
                name = field.group(1) if field else "_field"
                violations.append(
                    self.violation(
                        f'Test accesses private member "{name}". '
                        f"Verify behavior through the public API.",
                        location=str(file_path),
                        line=i,
                        severity="info",
                    )
                )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            ObservableBehaviorScanner,
            RULE,
            lambda root: sorted(p for p in root.rglob("*") if p.is_file()),
        )
    )
