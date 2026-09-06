"""Scanner for cover-all-behavior-paths rule in JavaScript/TypeScript.

Checks that test suites cover happy path, edge cases, and error paths.
Flags describe blocks that lack error/edge/boundary test cases.
"""

import re
from typing import List, Dict, Any, Set, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

DESCRIBE_RE = re.compile(
    r'''describe\s*\(\s*['"`](.+?)['"`]''', re.IGNORECASE
)
TEST_RE = re.compile(
    r'''(?:it|test)\s*\(\s*['"`](.+?)['"`]''', re.IGNORECASE
)
ERROR_KEYWORDS: Set[str] = {
    'error', 'invalid', 'edge', 'boundary', 'empty', 'null', 'undefined',
    'missing', 'fail', 'reject', 'throw', 'exception', 'negative',
    'malformed', 'bad', 'zero', 'overflow', 'timeout', 'not found',
    'unauthorized', 'forbidden',
}


class CoverAllPathsScanner(JSCodeScanner):

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

        describes = self._find_describe_blocks(lines)
        if not describes:
            return violations

        for desc_name, desc_line, test_names in describes:
            if not test_names:
                continue
            has_error_test = any(
                any(kw in name.lower() for kw in ERROR_KEYWORDS)
                for name in test_names
            )
            if not has_error_test:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'describe("{desc_name}") has {len(test_names)} test(s) but '
                        f'none cover error/edge/boundary paths. Add tests for '
                        f'invalid input, missing data, or error conditions.'
                    ),
                    location=str(file_path),
                    line_number=desc_line,
                    severity='warning'
                ).to_dict())
        return violations

    def _find_describe_blocks(self, lines):
        blocks = []
        current_desc = None
        current_line = 0
        current_tests = []
        depth = 0

        for i, line in enumerate(lines):
            dm = DESCRIBE_RE.search(line)
            if dm and depth == 0:
                if current_desc is not None:
                    blocks.append((current_desc, current_line, current_tests))
                current_desc = dm.group(1)
                current_line = i + 1
                current_tests = []
                depth = line.count('{') - line.count('}')
                continue

            if current_desc is not None:
                depth += line.count('{') - line.count('}')
                tm = TEST_RE.search(line)
                if tm:
                    current_tests.append(tm.group(1))
                if depth <= 0:
                    blocks.append((current_desc, current_line, current_tests))
                    current_desc = None
                    current_tests = []
                    depth = 0

        if current_desc is not None:
            blocks.append((current_desc, current_line, current_tests))
        return blocks
