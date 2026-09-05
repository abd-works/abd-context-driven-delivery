"""Scanner for class-based test organization in JavaScript/TypeScript.

Checks that test files use describe() blocks to group tests by behavior.
Flags files with only top-level it()/test() calls without describe() grouping.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

DESCRIBE_RE = re.compile(r'^\s*describe\s*\(', re.MULTILINE)
TOP_LEVEL_TEST_RE = re.compile(r'^(?:it|test)\s*\(', re.MULTILINE)


class ClassBasedOrganizationScanner(JSCodeScanner):

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')):
            return violations
        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations
        lines = content.split('\n')

        has_describe = bool(DESCRIBE_RE.search(content))
        orphan_tests = []

        for i, line in enumerate(lines):
            if TOP_LEVEL_TEST_RE.match(line):
                orphan_tests.append(i + 1)

        if orphan_tests and not has_describe:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    f'Test file has {len(orphan_tests)} top-level test()/it() call(s) '
                    f'without any describe() grouping. Organize tests into describe() '
                    f'blocks that mirror behavior areas or story names.'
                ),
                location=str(file_path),
                line_number=orphan_tests[0],
                severity='warning'
            ).to_dict())
        elif orphan_tests and has_describe:
            for line_no in orphan_tests:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Top-level test at line {line_no} sits outside any describe() '
                        f'block — move it into the appropriate describe() group.'
                    ),
                    location=str(file_path),
                    line_number=line_no,
                    severity='warning'
                ).to_dict())
        return violations
