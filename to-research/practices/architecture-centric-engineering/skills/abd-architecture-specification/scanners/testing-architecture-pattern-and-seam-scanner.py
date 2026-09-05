#!/usr/bin/env python3
"""Flag test-helpers context files that are missing a named pattern or stub boundary.

The test-helpers architecture-context.md must declare two facts explicitly:

  1. **Pattern** — the testing strategy in use (e.g. Sandbox, Unit+Integration,
     Component-test pyramid, BDD via Gherkin).
  2. **Stub boundary** — the exact layer at which external systems are replaced
     (e.g. "stubbed at the axios.request boundary in /tests/helpers/axios-sandbox.ts").

Without both facts a new engineer cannot write a test that fits the existing suite.

A "test context file" is any architecture-context.md located inside a directory
whose path contains 'test', 'tests', 'testing', 'test-helpers', or 'test_helpers'.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

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
from arch_spec_context import build_arch_spec_context, is_test_context  # noqa: E402

# "Pattern:" (with or without bold markers) followed by any content on that line
_PATTERN_DECL_RE = re.compile(
    r"\*{0,2}pattern\*{0,2}\s*:",
    re.IGNORECASE,
)

# "Stub boundary:", "Stub:" followed by any content, or "stubbed at the"
_STUB_BOUNDARY_RE = re.compile(
    r"(?:\*{0,2}stub(?:\s+boundary)?\*{0,2}\s*:|stubbed\s+at\s+the\b)",
    re.IGNORECASE,
)


class TestingArchitecturePatternAndSeamScanner(Scanner):

    def scan_file_with_context(self, context: FileScanContext) -> List[dict]:
        if not context.exists:
            return []
        if not is_test_context(context.file_path):
            return []

        text = context.file_path.read_text(encoding="utf-8")
        violations: List[dict] = []

        has_pattern = bool(_PATTERN_DECL_RE.search(text))
        has_stub_boundary = bool(_STUB_BOUNDARY_RE.search(text))

        if not has_pattern:
            violations.append(
                Violation(
                    rule=self.rule,
                    violation_message=(
                        f"Test-helpers context file '{context.file_path.name}' is missing a "
                        f"named testing pattern. Add a line like "
                        f"'**Pattern:** Sandbox. Domain fixtures drive the real Express app via Jest + Supertest.' "
                        f"so engineers know which strategy the suite follows."
                    ),
                    location=str(context.file_path),
                    severity="error",
                ).to_dict()
            )

        if not has_stub_boundary:
            violations.append(
                Violation(
                    rule=self.rule,
                    violation_message=(
                        f"Test-helpers context file '{context.file_path.name}' is missing a "
                        f"named stub boundary. Add a line like "
                        f"'**Stub boundary:** outbound HTTP stubbed at axios.request in /tests/helpers/axios-sandbox.ts.' "
                        f"so engineers know where the real system ends and stubs begin."
                    ),
                    location=str(context.file_path),
                    severity="error",
                ).to_dict()
            )

        return violations


if __name__ == "__main__":
    sys.exit(
        execute_scan_with_workspace(
            TestingArchitecturePatternAndSeamScanner,
            "testing-architecture-names-pattern-and-seam",
            build_arch_spec_context,
            skill_root=_ROOT,
        )
    )
