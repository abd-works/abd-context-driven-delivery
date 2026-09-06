"""
Scanner: example_data_alignment

Detects test data values that look invented rather than derived from
specification Examples tables.

Flags:
  - Common placeholder strings used as email/password/id in test functions.
  - Inline domain-looking emails or IDs without a fixtures/conftest import.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from code_scanner import CodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_PY_EXTS = ('.py',)

_PLACEHOLDER_EMAIL = re.compile(
    r"""['\"](test@example\.com|user@example\.com|foo@bar\.com|admin@test\.com|"""
    r"""fake@[^'\"]+|demo@[^'\"]+|noreply@[^'\"]+)['\"]""",
    re.IGNORECASE,
)

_PLACEHOLDER_PASSWORD = re.compile(
    r"""['\"](password1?[!1]?|pass123|secret|admin123|abc123|letmein|"""
    r"""test123|qwerty|password[_\-]?\d*)['\"]""",
    re.IGNORECASE,
)

_PLACEHOLDER_ID = re.compile(
    r"""['\"](foo|bar|baz|test[-_]?id|fake[-_]?id|123|456|dummy|stub[-_]?id[-_]?\d*)['\"]""",
    re.IGNORECASE,
)

_FIXTURES_IMPORT = re.compile(
    r"""(?:from|import)\s+[^\n]*(?:fixtures|conftest|constants|seeds|test_data)""",
    re.IGNORECASE,
)

_INLINE_DOMAIN_EMAIL = re.compile(
    r"""['\"']([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})['\"]"""
)

_TEST_FUNC = re.compile(r'^\s*def\s+test_')


class ExampleDataAlignmentScanner(CodeScanner):
    """
    Detects invented / placeholder test data that should be derived from
    specification Examples tables and imported from a shared fixtures file.
    """

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in _PY_EXTS):
            return violations
        if not self._is_test_file(path_str):
            return violations
        if any(x in path_str for x in ('fixtures', 'conftest', 'constants', 'seeds')):
            return violations

        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations

        has_fixtures_import = bool(_FIXTURES_IMPORT.search(content))
        lines = content.split('\n')
        in_test = False
        inline_emails: list[tuple[int, str]] = []

        for line_num, line in enumerate(lines, 1):
            if _TEST_FUNC.match(line):
                in_test = True
            if not in_test:
                continue

            m = _PLACEHOLDER_EMAIL.search(line)
            if m:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Placeholder email "{m.group(1)}" at line {line_num}. '
                        'Use a value from the specification Examples table, '
                        'imported from conftest or a fixtures file.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='error',
                ).to_dict())
                continue

            m = _PLACEHOLDER_PASSWORD.search(line)
            if m:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Placeholder password "{m.group(1)}" at line {line_num}. '
                        'Import the stub password constant from conftest '
                        'or use the value named in the spec Examples.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='error',
                ).to_dict())
                continue

            m = _PLACEHOLDER_ID.search(line)
            if m:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Generic placeholder "{m.group(1)}" at line {line_num}. '
                        'Use the identifier from the specification Examples table.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='warning',
                ).to_dict())
                continue

            m = _INLINE_DOMAIN_EMAIL.search(line)
            if m and not has_fixtures_import:
                inline_emails.append((line_num, m.group(1)))

        for line_num, email in inline_emails:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    f'Domain email "{email}" typed inline at line {line_num} '
                    'without a fixtures import. Extract to conftest and import the constant.'
                ),
                location=str(file_path),
                line_number=line_num,
                severity='warning',
            ).to_dict())

        return violations

    def _is_test_file(self, path_str: str) -> bool:
        return 'test_' in path_str or '_test' in path_str or '/test' in path_str or '\\test' in path_str
