"""Scanner for Given/When/Then helper extraction in JavaScript/TypeScript.

Checks for long inline test setup (>4 lines before first assertion).
Flags tests without helper function extraction and repeated setup patterns
that should be extracted into given_/when_/then_ helpers.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

TEST_BLOCK_RE = re.compile(
    r'''(?:it|test)\s*\(\s*['"`](.+?)['"`]\s*,''', re.IGNORECASE
)
ASSERTION_RE = re.compile(
    r'(?:expect\s*\(|assert[\.\(]|should[\.\(])', re.IGNORECASE
)
HELPER_CALL_RE = re.compile(
    r'\b(?:given_|when_|then_|create_|verify_|setup_|build_)\w+\s*\('
)
MAX_INLINE_SETUP = 4


class GivenWhenThenHelpersScanner(JSCodeScanner):

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

        test_blocks = self._find_test_bodies(lines)
        for test_name, start_line, body_lines in test_blocks:
            setup_count = self._count_setup_lines(body_lines)
            if setup_count > MAX_INLINE_SETUP:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test "{test_name}" has {setup_count} inline setup lines '
                        f'before the first assertion (max {MAX_INLINE_SETUP}). '
                        f'Extract setup into given_/when_ helper functions.'
                    ),
                    location=str(file_path),
                    line_number=start_line,
                    severity='warning'
                ).to_dict())
        return violations

    def _find_test_bodies(self, lines):
        blocks = []
        i = 0
        while i < len(lines):
            m = TEST_BLOCK_RE.search(lines[i])
            if m:
                test_name = m.group(1)
                start = i + 1
                depth = lines[i].count('{') - lines[i].count('}')
                if depth <= 0 and '{' not in lines[i]:
                    i += 1
                    continue
                body_lines = []
                j = i + 1
                while j < len(lines) and depth > 0:
                    depth += lines[j].count('{') - lines[j].count('}')
                    body_lines.append(lines[j])
                    j += 1
                blocks.append((test_name, start, body_lines))
                i = j
                continue
            i += 1
        return blocks

    def _count_setup_lines(self, body_lines):
        setup_count = 0
        for line in body_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped == '}' or stripped == '});':
                continue
            if ASSERTION_RE.search(stripped):
                break
            if HELPER_CALL_RE.search(stripped):
                continue
            setup_count += 1
        return setup_count
