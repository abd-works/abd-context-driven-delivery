"""Scanner for detecting defensive guard clauses in test code."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

_GUARD_RETURN = re.compile(
    r'if\s*\(\s*!?\w[\w.]*\s*\)\s*(?:return|continue|break)'
)

_TRY_CATCH_SWALLOW = re.compile(
    r'catch\s*\([^)]*\)\s*\{[\s\n]*\}'
)

_OPTIONAL_CHAIN_IN_ASSERT = re.compile(
    r'expect\s*\([^)]*\?\.[^)]*\)'
)

_EARLY_RETURN_GUARD = re.compile(
    r'if\s*\(\s*(?:!result|!response|!data|!output|result\s*===?\s*(?:null|undefined)|'
    r'response\s*===?\s*(?:null|undefined))\s*\)\s*(?:\{?\s*return)'
)

_CATCH_IGNORE = re.compile(
    r'catch\s*\(\s*\w*\s*\)\s*\{\s*(?://.*)?(?:\s*(?:return|continue|break)\s*;?)?\s*\}'
)


class NoGuardClausesScanner(JSCodeScanner):
    """Detects defensive code in tests — tests should fail fast, not guard defensively."""

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

            if _EARLY_RETURN_GUARD.search(stripped) or _GUARD_RETURN.search(stripped):
                if 'expect' not in stripped:
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            'Guard clause in test: tests should fail on unexpected null/undefined, '
                            'not silently return.'
                        ),
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict())

            if _OPTIONAL_CHAIN_IN_ASSERT.search(stripped):
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        'Optional chaining (?.) inside expect(). '
                        'Assert the object exists first, then assert its property.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='warning'
                ).to_dict())

        for m in _CATCH_IGNORE.finditer(content):
            pos = content[:m.start()].count('\n') + 1
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    'Empty or swallowed catch block in test. '
                    'Let exceptions propagate so the test fails visibly.'
                ),
                location=str(file_path),
                line_number=pos,
                severity='warning'
            ).to_dict())

        return violations

    def _is_test_file(self, path_str: str) -> bool:
        return any(marker in path_str for marker in (
            '.test.', '.spec.', '__tests__', '/test/', '\\test\\'
        ))
