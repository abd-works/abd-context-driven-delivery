"""Scanner for Playwright locator anti-patterns in E2E test helpers and specs."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path

from scanner_bases.scanner import Scanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import ScanFilesContext, FileScanContext


class PlaywrightLocatorAntiPatternsScanner(Scanner):
    """Detects common Playwright anti-patterns:
    - waitForLoadState('networkidle')
    - :visible in CSS selectors
    - getByDisplayValue (Testing Library, not Playwright)
    """

    E2E_FILE_PATTERNS = [
        r'\.spec\.ts$',
        r'\.spec\.js$',
        r'-helper\.ts$',
        r'-helper\.js$',
        r'helpers?\.ts$',
        r'helpers?\.js$',
        r'global[-_]?setup\.',
    ]

    def scan_with_context(self, context: 'ScanFilesContext') -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        for file_path in context.file_paths:
            if self._is_e2e_file(file_path):
                violations.extend(self._scan_file(file_path))
        return violations

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        if self._is_e2e_file(context.file_path):
            return self._scan_file(context.file_path)
        return []

    def _is_e2e_file(self, file_path: Path) -> bool:
        name = file_path.name
        return any(re.search(pat, name) for pat in self.E2E_FILE_PATTERNS)

    def _scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        try:
            content = file_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return violations

        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue

            if 'networkidle' in line and 'waitForLoadState' in line:
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=(
                            "waitForLoadState('networkidle') — flaky under parallel workers. "
                            "Wait for a specific element with .waitFor() instead."
                        ),
                        line_number=i,
                        location=str(file_path),
                        severity='error',
                    ).to_dict()
                )

            if ':visible' in line and ('locator(' in line or "querySelector" in line):
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=(
                            ":visible is not a valid CSS pseudo-class. "
                            "Use [data-state=\"active\"] or .filter({ hasText }) instead."
                        ),
                        line_number=i,
                        location=str(file_path),
                        severity='error',
                    ).to_dict()
                )

            if 'getByDisplayValue' in line:
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=(
                            "getByDisplayValue is a Testing Library API, not Playwright. "
                            "Use page.waitForFunction() or page.locator('input') with a value check."
                        ),
                        line_number=i,
                        location=str(file_path),
                        severity='error',
                    ).to_dict()
                )

        return violations
