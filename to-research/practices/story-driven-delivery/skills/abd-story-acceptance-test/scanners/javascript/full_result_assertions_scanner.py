"""Scanner for full result assertions in JavaScript/TypeScript test files.

Detects assertions that only check single fields (expect(result.id).toBe(...))
when full object matching or deep equality would be more appropriate.
"""

import re
from typing import List, Dict, Any, Set, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

TARGET_NAMES: Set[str] = {
    'result', 'results', 'response', 'resp', 'payload', 'data',
    'output', 'details', 'info', 'state', 'config', 'event',
    'activity', 'record', 'entry',
}

SINGLE_FIELD_RE = re.compile(
    r'expect\s*\(\s*(\w+)\s*\.\s*(\w+)\s*\)\s*\.\s*(?:toBe|toEqual|toStrictEqual|toBeTruthy|toBeFalsy)\s*\(',
)
FULL_ASSERT_RE = re.compile(
    r'expect\s*\(\s*(\w+)\s*\)\s*\.\s*(?:toEqual|toStrictEqual|toMatchObject)\s*\(',
)


class FullResultAssertionsScanner(JSCodeScanner):

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

        full_assert_targets = set()
        for line in lines:
            m = FULL_ASSERT_RE.search(line)
            if m and m.group(1).lower() in TARGET_NAMES:
                full_assert_targets.add(m.group(1))

        for i, line in enumerate(lines):
            m = SINGLE_FIELD_RE.search(line)
            if not m:
                continue
            var_name = m.group(1)
            field_name = m.group(2)
            if var_name.lower() not in TARGET_NAMES:
                continue
            if var_name in full_assert_targets:
                continue
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    f'Assertion checks only "{var_name}.{field_name}" — '
                    f'assert the full domain object with toEqual()/toMatchObject() '
                    f'using standard test data instead of checking fields one by one'
                ),
                location=str(file_path),
                line_number=i + 1,
                severity='warning'
            ).to_dict())
        return violations
