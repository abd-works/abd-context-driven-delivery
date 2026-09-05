"""Scanner for idempotent test data setup in E2E global-setup files."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path

from scanner_bases.scanner import Scanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import ScanFilesContext, FileScanContext


class IdempotentSetupScanner(Scanner):
    """Checks that E2E setup scripts clean transient data before seeding
    and that upsert update blocks don't omit fields present in create blocks."""

    SETUP_FILE_PATTERNS = [
        r'global[-_]?setup',
        r'seed',
        r'fixtures',
        r'test[-_]?setup',
    ]

    def scan_with_context(self, context: 'ScanFilesContext') -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        for file_path in context.file_paths:
            if self._is_setup_file(file_path):
                violations.extend(self._scan_setup_file(file_path))
        return violations

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        if self._is_setup_file(context.file_path):
            return self._scan_setup_file(context.file_path)
        return []

    def _is_setup_file(self, file_path: Path) -> bool:
        stem = file_path.stem.lower().replace('-', '').replace('_', '')
        return any(
            re.search(pattern.replace('-', '').replace('_', ''), stem)
            for pattern in self.SETUP_FILE_PATTERNS
        )

    def _scan_setup_file(self, file_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        try:
            content = file_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return violations

        lines = content.split('\n')

        self._check_networkidle(file_path, lines, violations)
        self._check_upsert_update_completeness(file_path, content, lines, violations)
        self._check_hardcoded_near_dates(file_path, lines, violations)

        return violations

    def _check_networkidle(self, file_path: Path, lines: List[str], violations: List[Dict[str, Any]]) -> None:
        for i, line in enumerate(lines, 1):
            if 'networkidle' in line and 'waitForLoadState' in line:
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message="waitForLoadState('networkidle') found — use a targeted element waitFor() instead.",
                        line_number=i,
                        location=str(file_path),
                        severity='warning',
                    ).to_dict()
                )

    def _check_upsert_update_completeness(
        self, file_path: Path, content: str, lines: List[str], violations: List[Dict[str, Any]]
    ) -> None:
        upsert_pattern = re.compile(r'\.upsert\s*\(', re.MULTILINE)
        for match in upsert_pattern.finditer(content):
            line_number = content[:match.start()].count('\n') + 1
            block_start = match.start()
            block_end = self._find_matching_brace(content, block_start)
            if block_end == -1:
                continue
            block = content[block_start:block_end]

            create_fields = self._extract_object_keys(block, 'create')
            update_fields = self._extract_object_keys(block, 'update')

            if create_fields and update_fields:
                missing = create_fields - update_fields - {'id', 'where', 'code'}
                if missing:
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=(
                                f"Upsert update block is missing fields present in create: "
                                f"{', '.join(sorted(missing))}. "
                                f"Re-runs will leave stale values."
                            ),
                            line_number=line_number,
                            location=str(file_path),
                            severity='warning',
                        ).to_dict()
                    )

    def _check_hardcoded_near_dates(self, file_path: Path, lines: List[str], violations: List[Dict[str, Any]]) -> None:
        date_pattern = re.compile(r"""['"](\d{4})-(\d{2})-(\d{2})['"]""")
        for i, line in enumerate(lines, 1):
            if 'endAt' not in line and 'end_at' not in line:
                continue
            match = date_pattern.search(line)
            if match:
                year = int(match.group(1))
                if 2024 <= year <= 2030:
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=(
                                f"endAt uses a near-future date ({match.group(0)}). "
                                f"Use 2099-12-31 or null for evergreen test fixtures."
                            ),
                            line_number=i,
                            location=str(file_path),
                            severity='warning',
                        ).to_dict()
                    )

    def _find_matching_brace(self, content: str, start: int) -> int:
        depth = 0
        i = content.find('(', start)
        if i == -1:
            return -1
        for j in range(i, min(i + 5000, len(content))):
            if content[j] == '(':
                depth += 1
            elif content[j] == ')':
                depth -= 1
                if depth == 0:
                    return j + 1
        return -1

    def _extract_object_keys(self, block: str, label: str) -> set:
        pattern = re.compile(rf'{label}\s*:\s*\{{([^}}]*)\}}', re.DOTALL)
        match = pattern.search(block)
        if not match:
            return set()
        body = match.group(1)
        keys = re.findall(r'(\w+)\s*:', body)
        return set(keys)
