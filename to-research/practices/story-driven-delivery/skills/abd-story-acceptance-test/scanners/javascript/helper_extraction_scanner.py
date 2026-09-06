"""Scanner for detecting repeated setup/assertion patterns that should be extracted to helpers."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')
_TEST_FN = re.compile(
    r'^\s*(?:it|test)\s*\(\s*[\'"`]', re.MULTILINE
)
_ASSERTION = re.compile(
    r'\b(?:expect|assert|should)\s*[\.(]'
)
_SETUP_LINE = re.compile(
    r'^\s*(?:const|let|var)\s+\w+\s*=|'
    r'^\s*\w+\s*\.\s*(?:set|add|push|create|init|configure|reset|clear|prepare)|'
    r'^\s*(?:await\s+)?\w+\s*=',
    re.MULTILINE
)


class HelperExtractionScanner(JSCodeScanner):
    """Detects test functions with excessive inline setup that should be extracted to helpers."""

    MAX_SETUP_LINES = 4

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in _JS_EXTS):
            return violations
        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations

        blocks = self._extract_test_blocks(content)
        setup_fingerprints: List[tuple] = []

        for name, body, start_line in blocks:
            setup_lines = self._count_setup_before_assertion(body)
            if setup_lines > self.MAX_SETUP_LINES:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test "{name}" has {setup_lines} setup lines before its first assertion '
                        f'(max {self.MAX_SETUP_LINES}). Extract setup into a helper function.'
                    ),
                    location=str(file_path),
                    line_number=start_line,
                    severity='warning'
                ).to_dict())

            fp = self._setup_fingerprint(body)
            if fp:
                for prev_fp, prev_name, prev_line in setup_fingerprints:
                    if self._fingerprints_overlap(fp, prev_fp):
                        violations.append(Violation(
                            rule=self.rule,
                            violation_message=(
                                f'Test "{name}" duplicates setup from "{prev_name}" (line {prev_line}). '
                                'Extract shared setup into a helper.'
                            ),
                            location=str(file_path),
                            line_number=start_line,
                            severity='warning'
                        ).to_dict())
                        break
                setup_fingerprints.append((fp, name, start_line))

        return violations

    def _extract_test_blocks(self, content: str):
        lines = content.split('\n')
        blocks = []
        for i, line in enumerate(lines):
            m = re.match(r'^\s*(?:it|test)\s*\(\s*[\'"`]([^\'"`]+)', line)
            if not m:
                continue
            name = m.group(1)
            depth, body_lines = 0, []
            for j in range(i, min(i + 80, len(lines))):
                depth += lines[j].count('{') + lines[j].count('(') - lines[j].count('}') - lines[j].count(')')
                body_lines.append(lines[j])
                if depth <= 0 and j > i:
                    break
            blocks.append((name, '\n'.join(body_lines), i + 1))
        return blocks

    def _count_setup_before_assertion(self, body: str) -> int:
        count = 0
        for line in body.split('\n')[1:]:
            stripped = line.strip()
            if not stripped or stripped.startswith('//'):
                continue
            if _ASSERTION.search(stripped):
                break
            if _SETUP_LINE.match(stripped):
                count += 1
        return count

    def _setup_fingerprint(self, body: str) -> tuple:
        tokens = []
        for line in body.split('\n')[1:]:
            stripped = line.strip()
            if _ASSERTION.search(stripped):
                break
            if _SETUP_LINE.match(stripped):
                normalised = re.sub(r'[\'"`][^\'"`]*[\'"`]', 'STR', stripped)
                normalised = re.sub(r'\d+', 'NUM', normalised)
                tokens.append(normalised)
        return tuple(tokens) if len(tokens) >= 2 else ()

    def _fingerprints_overlap(self, a: tuple, b: tuple) -> bool:
        if not a or not b:
            return False
        shared = sum(1 for x in a if x in b)
        return shared >= 2 and shared >= len(min(a, b, key=len)) * 0.6
