"""Scanner: `layer-isolation` — mock only architecture boundaries.

Rule: layer-isolation

Mocks belong at the edge of the layer under test (APIs, repositories, FS,
third-party services). Mocking relative internal modules or domain helpers
proves nothing about the subject.

Adapted from abd-skills abd-bdd-development `mock_boundaries_scanner.py`
(JS-only) for Jest/Vitest plus Python unittest.mock / pytest-mock.
"""
from __future__ import annotations

import re
from pathlib import Path

from scan import Scanner, ScannerRunner

from bdd_scan_helpers import is_spec_file, read_text

RULE = "layer-isolation"

_MOCK_CALL = re.compile(
    r"(?:jest\.mock|jest\.spyOn|vi\.mock|vi\.spyOn|sinon\.stub|"
    r"mocker\.patch|unittest\.mock\.patch|@patch)\s*\(",
    re.IGNORECASE,
)
_INTERNAL_NAMES = re.compile(
    r"\b(?:validate|calculate|process|format|parse|helper|util|transform|"
    r"convert|normalize|sanitize|build|create|make|compose)\b",
    re.IGNORECASE,
)
_RELATIVE_MODULE = re.compile(
    r"""(?:jest\.mock|vi\.mock|mocker\.patch|unittest\.mock\.patch|@patch)"""
    r"""\s*\(\s*['"]\./"""
)


class LayerIsolationScanner(Scanner):
    """Flag mocks that target internal code instead of layer boundaries."""

    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if not is_spec_file(file_path):
            return []
        content = read_text(file_path)
        if not content:
            return []

        violations = []
        for i, line in enumerate(content.splitlines(), 1):
            if not _MOCK_CALL.search(line):
                continue

            if _INTERNAL_NAMES.search(line):
                word = _INTERNAL_NAMES.search(line).group(0)
                violations.append(
                    self.violation(
                        f'Mock targets internal function "{word}". '
                        f"Only mock external boundaries "
                        f"(APIs, databases, third-party services).",
                        location=str(file_path),
                        line=i,
                        severity="warning",
                    )
                )
                continue

            if _RELATIVE_MODULE.search(line):
                mod = re.search(r"""['"](\./[^'"]+)['"]""", line)
                name = mod.group(1) if mod else "relative module"
                violations.append(
                    self.violation(
                        f'Mock on relative module "{name}". '
                        f"Prefer mocking external boundaries; "
                        f"call internal code directly.",
                        location=str(file_path),
                        line=i,
                        severity="warning",
                    )
                )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            LayerIsolationScanner,
            RULE,
            lambda root: sorted(p for p in root.rglob("*") if p.is_file()),
        )
    )
