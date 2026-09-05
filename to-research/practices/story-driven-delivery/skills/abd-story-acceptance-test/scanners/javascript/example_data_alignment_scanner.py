"""
Scanner: example_data_alignment

Detects test data values that look invented rather than derived from
specification Examples tables.

Flags:
  - Common placeholder strings used as email/password/id in test files
    that are not imported from a shared fixtures/constants file.
  - Raw domain-looking string literals duplicated across test blocks
    without a fixtures import present in the file.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

# Patterns that strongly suggest invented / placeholder data
_PLACEHOLDER_EMAIL = re.compile(
    r"""['"`](test@example\.com|user@example\.com|foo@bar\.com|admin@test\.com|"""
    r"""fake@[^'"`]+|demo@[^'"`]+|noreply@[^'"`]+)['"`]""",
    re.IGNORECASE,
)

_PLACEHOLDER_PASSWORD = re.compile(
    r"""['"`](password1?[!1]?|pass123|secret|admin123|abc123|letmein|"""
    r"""test123|qwerty|password[_\-]?\d*)['"`]""",
    re.IGNORECASE,
)

_PLACEHOLDER_ID = re.compile(
    r"""['"`](foo|bar|baz|test[-_]?id|fake[-_]?id|123|456|dummy|stub[-_]?id[-_]?\d*)['"`]""",
    re.IGNORECASE,
)

# A file has a fixtures import if it imports from a fixtures/constants/conftest file
_FIXTURES_IMPORT = re.compile(
    r"""import\s+.*?from\s+['"`][^'"`]*(?:fixtures|constants|conftest|seeds|test[-_]?data)['"`]""",
    re.IGNORECASE,
)

# Inline domain string: looks like a real email/ID but is typed raw
_INLINE_DOMAIN_EMAIL = re.compile(
    r"""['"`]([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})['"`]"""
)

_TEST_BLOCK = re.compile(
    r"""^\s*(?:it|test)(?:\.only|\.skip)?\s*\(""",
)


class ExampleDataAlignmentScanner(JSCodeScanner):
    """
    Detects test data values that are invented rather than derived from
    specification Examples tables or a shared fixtures file.
    """

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in _JS_EXTS):
            return violations
        if not self._is_test_file(path_str):
            return violations
        # Skip fixture files themselves
        if any(x in path_str for x in ('fixtures', 'constants', 'conftest', 'seeds')):
            return violations

        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations

        has_fixtures_import = bool(_FIXTURES_IMPORT.search(content))

        lines = content.split('\n')
        in_test_block = False
        inline_emails: list[tuple[int, str]] = []

        for line_num, line in enumerate(lines, 1):
            if _TEST_BLOCK.match(line):
                in_test_block = True

            if not in_test_block:
                continue

            # Placeholder emails
            m = _PLACEHOLDER_EMAIL.search(line)
            if m:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Placeholder email "{m.group(1)}" at line {line_num}. '
                        'Use a value from the specification Examples table, '
                        'imported via a shared fixtures file.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='error',
                ).to_dict())
                continue

            # Placeholder passwords
            m = _PLACEHOLDER_PASSWORD.search(line)
            if m:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Placeholder password "{m.group(1)}" at line {line_num}. '
                        'Import the stub password constant from the fixtures file '
                        'or use the value named in the spec Examples.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='error',
                ).to_dict())
                continue

            # Placeholder IDs / tokens
            m = _PLACEHOLDER_ID.search(line)
            if m:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Generic placeholder "{m.group(1)}" at line {line_num}. '
                        'Use the identifier from the specification Examples table '
                        'imported from the fixtures file.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='warning',
                ).to_dict())
                continue

            # Inline domain email not imported from fixtures
            m = _INLINE_DOMAIN_EMAIL.search(line)
            if m and not has_fixtures_import:
                email = m.group(1)
                inline_emails.append((line_num, email))

        # Report inline domain emails when no fixtures import exists
        for line_num, email in inline_emails:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    f'Domain email "{email}" typed inline at line {line_num} '
                    'without a fixtures import. Extract to a shared fixtures file '
                    'and import the constant.'
                ),
                location=str(file_path),
                line_number=line_num,
                severity='warning',
            ).to_dict())

        return violations

    def _is_test_file(self, path_str: str) -> bool:
        return any(marker in path_str for marker in (
            '.test.', '.spec.', '__tests__', '/test/', '\\test\\'
        ))
