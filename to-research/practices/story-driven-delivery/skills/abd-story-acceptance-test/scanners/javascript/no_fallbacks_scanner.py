"""Scanner for detecting silent fallback patterns in test code."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

_OR_DEFAULT = re.compile(
    r'\|\|\s*(?:[\'"`\[\{]|true|false|null|undefined|\d+|new\s)'
)

_NULLISH_COALESCE = re.compile(r'\?\?\s*(?:[\'"`\[\{]|true|false|null|undefined|\d+|new\s)')

_TERNARY_DEFAULT = re.compile(
    r'\?\s*\w[\w.]*\s*:\s*(?:[\'"`\[\{]|true|false|null|undefined|\d+|new\s)'
)

_DEFAULT_PARAM = re.compile(
    r'(?:const|let|var)\s+\{[^}]*=\s*(?:[\'"`]|true|false|\d+|null|\[\]|\{\})'
)


class NoFallbacksScanner(JSCodeScanner):
    """Detects fallback/default-value patterns in tests — tests should fail explicitly."""

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
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('//'):
                continue

            if _OR_DEFAULT.search(stripped):
                violations.append(self._make_violation(
                    '|| default', file_path, line_num,
                    'Test uses || fallback. Tests should fail explicitly, not provide silent defaults.'
                ))
            elif _NULLISH_COALESCE.search(stripped):
                violations.append(self._make_violation(
                    '?? default', file_path, line_num,
                    'Test uses ?? nullish coalescing fallback. Tests should fail explicitly on null/undefined.'
                ))
            elif _TERNARY_DEFAULT.search(stripped):
                if 'expect' not in stripped:
                    violations.append(self._make_violation(
                        'ternary default', file_path, line_num,
                        'Test uses ternary fallback. Let the test fail if the value is unexpected.'
                    ))
            elif _DEFAULT_PARAM.search(stripped):
                violations.append(self._make_violation(
                    'destructuring default', file_path, line_num,
                    'Test uses destructuring defaults. Tests should assert exact structure, not fill in gaps.'
                ))

        return violations

    def _is_test_file(self, path_str: str) -> bool:
        return any(marker in path_str for marker in (
            '.test.', '.spec.', '__tests__', '/test/', '\\test\\'
        ))

    def _make_violation(self, kind: str, file_path: Path, line_num: int, msg: str):
        return Violation(
            rule=self.rule,
            violation_message=msg,
            location=str(file_path),
            line_number=line_num,
            severity='warning'
        ).to_dict()
