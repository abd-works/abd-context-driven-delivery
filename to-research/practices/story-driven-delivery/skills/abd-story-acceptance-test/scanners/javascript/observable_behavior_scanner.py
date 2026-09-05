"""Scanner for detecting assertions on private/internal state in tests."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

_EXPECT_PRIVATE = re.compile(
    r'expect\s*\([^)]*\._\w+'
)

_EXPECT_INTERNAL_ARRAY = re.compile(
    r'expect\s*\([^)]*\.(?:_\w+|__\w+)\s*(?:\[|\.length|\.includes|\.find)'
)

_DIRECT_PRIVATE_ACCESS = re.compile(
    r'(?:result|output|instance|obj|subject|sut)\s*\.\s*_\w+'
)

_PRIVATE_METHOD_CALL = re.compile(
    r'(?:result|output|instance|obj|subject|sut)\s*\.\s*_\w+\s*\('
)


class ObservableBehaviorScanner(JSCodeScanner):
    """Detects assertions on private/internal state — tests should assert observable behavior."""

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

            if _EXPECT_PRIVATE.search(stripped):
                field = re.search(r'\._(\w+)', stripped)
                name = field.group(1) if field else 'private field'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Assertion accesses private field "_{name}". '
                        'Assert observable behavior through public API instead.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='warning'
                ).to_dict())
                continue

            if _EXPECT_INTERNAL_ARRAY.search(stripped):
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        'Assertion accesses internal collection. '
                        'Assert through public query methods instead of reaching into private state.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='warning'
                ).to_dict())
                continue

            if _PRIVATE_METHOD_CALL.search(stripped):
                method = re.search(r'\.(_\w+)\s*\(', stripped)
                name = method.group(1) if method else '_method'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test calls private method "{name}". '
                        'Test through the public interface to verify observable behavior.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='warning'
                ).to_dict())
                continue

            if _DIRECT_PRIVATE_ACCESS.search(stripped) and 'expect' not in stripped:
                field = re.search(r'\.(_\w+)', stripped)
                name = field.group(1) if field else '_field'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test accesses private member "{name}". '
                        'Verify behavior through the public API.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='info'
                ).to_dict())

        return violations

    def _is_test_file(self, path_str: str) -> bool:
        return any(marker in path_str for marker in (
            '.test.', '.spec.', '__tests__', '/test/', '\\test\\'
        ))
