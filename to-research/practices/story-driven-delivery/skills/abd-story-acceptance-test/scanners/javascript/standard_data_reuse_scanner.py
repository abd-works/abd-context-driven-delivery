"""Scanner for detecting duplicated inline test data that should be shared constants."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

_OBJECT_LITERAL = re.compile(
    r'(?:const|let|var)\s+\w+\s*=\s*\{([^}]{15,})\}'
)

_TEST_BLOCK_START = re.compile(
    r'^\s*(?:it|test)\s*\(\s*[\'"`]'
)

_NOISE = re.compile(r'[\s\'"`]')


class StandardDataReuseScanner(JSCodeScanner):
    """Detects duplicated test data definitions that should be extracted to shared constants."""

    SIMILARITY_THRESHOLD = 0.75
    MIN_DUPLICATES = 2

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
        test_ranges = self._find_test_ranges(lines)
        literals = []

        for start, end in test_ranges:
            block = '\n'.join(lines[start:end])
            for m in _OBJECT_LITERAL.finditer(block):
                body = m.group(1).strip()
                keys = self._extract_keys(body)
                if len(keys) >= 2:
                    line_in_block = block[:m.start()].count('\n')
                    abs_line = start + line_in_block + 1
                    literals.append((keys, body, abs_line))

        reported = set()
        for i, (keys_a, body_a, line_a) in enumerate(literals):
            for j, (keys_b, body_b, line_b) in enumerate(literals):
                if j <= i:
                    continue
                if line_a == line_b:
                    continue
                if self._keys_similar(keys_a, keys_b):
                    key = (min(line_a, line_b), max(line_a, line_b))
                    if key in reported:
                        continue
                    reported.add(key)
                    shared = sorted(keys_a & keys_b)
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Similar object literals at lines {line_a} and {line_b} '
                            f'share keys [{", ".join(shared[:5])}]. '
                            'Extract to a shared constant or builder.'
                        ),
                        location=str(file_path),
                        line_number=line_a,
                        severity='warning'
                    ).to_dict())

        return violations

    def _find_test_ranges(self, lines):
        ranges = []
        i = 0
        while i < len(lines):
            if _TEST_BLOCK_START.match(lines[i]):
                start = i
                depth = 0
                for j in range(i, min(i + 100, len(lines))):
                    depth += lines[j].count('{') + lines[j].count('(')
                    depth -= lines[j].count('}') + lines[j].count(')')
                    if depth <= 0 and j > i:
                        ranges.append((start, j + 1))
                        i = j + 1
                        break
                else:
                    ranges.append((start, min(i + 50, len(lines))))
                    i += 1
            else:
                i += 1
        return ranges

    def _extract_keys(self, obj_body: str) -> set:
        return set(re.findall(r'(\w+)\s*:', obj_body))

    def _keys_similar(self, a: set, b: set) -> bool:
        if not a or not b:
            return False
        overlap = len(a & b)
        smaller = min(len(a), len(b))
        return overlap >= 2 and (overlap / smaller) >= self.SIMILARITY_THRESHOLD

    def _is_test_file(self, path_str: str) -> bool:
        return any(marker in path_str for marker in (
            '.test.', '.spec.', '__tests__', '/test/', '\\test\\'
        ))
