"""Scanner for detecting test functions that don't follow the orchestrator pattern."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

_TEST_BLOCK_START = re.compile(
    r'^\s*(?:it|test)\s*\(\s*[\'"`]([^\'"`]*)[\'"`]'
)

_DESCRIBE_START = re.compile(
    r'^\s*describe\s*\(\s*[\'"`]([^\'"`]*)[\'"`]'
)

MAX_TEST_BODY_LINES = 20
MAX_DESCRIBE_LINES = 120


class OrchestratorPatternScanner(JSCodeScanner):
    """Checks that test bodies are short orchestrators delegating to helper functions."""

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in _JS_EXTS):
            return violations
        if not self._is_test_file(path_str):
            return violations
        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations

        lines = content.split('\n')
        violations.extend(self._check_test_bodies(lines, file_path))
        violations.extend(self._check_describe_blocks(lines, file_path))
        return violations

    def _check_test_bodies(self, lines, file_path):
        violations = []
        i = 0
        while i < len(lines):
            m = _TEST_BLOCK_START.match(lines[i])
            if not m:
                i += 1
                continue
            test_name = m.group(1)
            start = i
            body_lines = self._count_block_body_lines(lines, i)
            if body_lines > MAX_TEST_BODY_LINES:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test "{test_name}" body is {body_lines} lines (max {MAX_TEST_BODY_LINES}). '
                        'Extract setup and assertions into named helper functions.'
                    ),
                    location=str(file_path),
                    line_number=start + 1,
                    severity='warning'
                ).to_dict())
            i += 1
        return violations

    def _check_describe_blocks(self, lines, file_path):
        violations = []
        i = 0
        while i < len(lines):
            m = _DESCRIBE_START.match(lines[i])
            if not m:
                i += 1
                continue
            desc_name = m.group(1)
            start = i
            block_lines = self._count_block_total_lines(lines, i)
            if block_lines > MAX_DESCRIBE_LINES:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'describe("{desc_name}") spans {block_lines} lines (max {MAX_DESCRIBE_LINES}). '
                        'Split into smaller describe blocks or extract helpers.'
                    ),
                    location=str(file_path),
                    line_number=start + 1,
                    severity='warning'
                ).to_dict())
            i += 1
        return violations

    def _count_block_body_lines(self, lines, start_idx):
        depth = 0
        body_count = 0
        started = False
        for i in range(start_idx, min(start_idx + 200, len(lines))):
            line = lines[i]
            opens = line.count('{') + line.count('(')
            closes = line.count('}') + line.count(')')
            depth += opens - closes
            if opens > 0 and not started:
                started = True
                continue
            if started:
                stripped = line.strip()
                if stripped and not stripped.startswith('//'):
                    body_count += 1
            if started and depth <= 0:
                break
        return body_count

    def _count_block_total_lines(self, lines, start_idx):
        depth = 0
        started = False
        for i in range(start_idx, min(start_idx + 500, len(lines))):
            depth += lines[i].count('{') - lines[i].count('}')
            if lines[i].count('{') > 0 and not started:
                started = True
            if started and depth <= 0:
                return i - start_idx + 1
        return len(lines) - start_idx

    def _is_test_file(self, path_str: str) -> bool:
        return any(marker in path_str for marker in (
            '.test.', '.spec.', '__tests__', '/test/', '\\test\\'
        ))
