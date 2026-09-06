"""Scanner for bug-fix-test-first rule in JavaScript/TypeScript.

Checks that test files for bug fixes contain RED-GREEN workflow indicators:
comments about reproduction, failure verification, or fix verification.
Flags bug/fix/regression-named tests that lack reproduction comments.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

BUG_NAME_RE = re.compile(
    r'(?:bug|fix|regression|broken|issue|patch|hotfix)', re.IGNORECASE
)
REPRODUCTION_RE = re.compile(
    r'(?://|/\*)\s*(?:reproduces?|bug|fix|regression|red|green|'
    r'expected\s+(?:fail|raise|error)|verify\s+.*(?:fail|pass))',
    re.IGNORECASE,
)
TEST_DECL_RE = re.compile(
    r'''(?:it|test)\s*\(\s*['"`](.+?)['"`]''', re.IGNORECASE
)


class BugFixTestFirstScanner(JSCodeScanner):

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

        for i, line in enumerate(lines):
            m = TEST_DECL_RE.search(line)
            if not m:
                continue
            test_name = m.group(1)
            if not BUG_NAME_RE.search(test_name):
                continue
            line_no = i + 1
            block_end = min(i + 30, len(lines))
            block_text = '\n'.join(lines[i:block_end])
            if not REPRODUCTION_RE.search(block_text):
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Bug-fix test "{test_name}" lacks reproduction comments. '
                        f'Follow RED-GREEN workflow: add a comment explaining which bug '
                        f'this reproduces and verify the test fails before the fix.'
                    ),
                    location=str(file_path),
                    line_number=line_no,
                    severity='warning'
                ).to_dict())
        return violations
