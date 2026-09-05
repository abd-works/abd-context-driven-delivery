"""Scanner for fixture placement in JavaScript/TypeScript test files.

Detects beforeEach/beforeAll patterns. Flags overly complex setup blocks
(>8 lines of logic) and shared fixtures imported from separate files when
they should be co-located.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

SETUP_RE = re.compile(r'(beforeEach|beforeAll|afterEach|afterAll)\s*\(', re.MULTILINE)
FIXTURE_IMPORT_RE = re.compile(
    r'''(?:import|require)\s*.*?['"].*?(?:fixture|helper|setup|factory|mock|fake).*?['"]''',
    re.IGNORECASE,
)
MAX_SETUP_LINES = 8


class FixturePlacementScanner(JSCodeScanner):

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

        violations.extend(self._check_setup_complexity(lines, file_path))
        violations.extend(self._check_fixture_imports(lines, file_path))
        return violations

    def _check_setup_complexity(self, lines, file_path):
        violations = []
        i = 0
        while i < len(lines):
            m = SETUP_RE.search(lines[i])
            if m:
                hook_name = m.group(1)
                hook_line = i + 1
                body_lines = self._count_body_lines(lines, i)
                if body_lines > MAX_SETUP_LINES:
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            f'{hook_name}() block at line {hook_line} has '
                            f'{body_lines} lines of setup (max {MAX_SETUP_LINES}). '
                            f'Extract complex setup into named helper functions.'
                        ),
                        location=str(file_path),
                        line_number=hook_line,
                        severity='warning'
                    ).to_dict())
            i += 1
        return violations

    def _count_body_lines(self, lines, start_idx):
        depth = 0
        count = 0
        started = False
        for i in range(start_idx, min(start_idx + 50, len(lines))):
            line = lines[i]
            depth += line.count('{') - line.count('}')
            if '{' in line and not started:
                started = True
                continue
            if started:
                stripped = line.strip()
                if stripped and not stripped.startswith('//'):
                    count += 1
                if depth <= 0:
                    break
        return count

    def _check_fixture_imports(self, lines, file_path):
        violations = []
        for i, line in enumerate(lines):
            if FIXTURE_IMPORT_RE.search(line):
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Line {i + 1} imports fixtures from a separate file. '
                        f'Co-locate test data with the test file, or use a '
                        f'shared factory only when 3+ files need the same data.'
                    ),
                    location=str(file_path),
                    line_number=i + 1,
                    severity='warning'
                ).to_dict())
        return violations
