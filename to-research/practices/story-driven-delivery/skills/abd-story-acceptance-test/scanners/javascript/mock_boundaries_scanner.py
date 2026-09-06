"""Scanner for detecting mocks of internal code rather than external boundaries."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

_MOCK_CALL = re.compile(
    r'(?:jest\.mock|jest\.spyOn|sinon\.stub|sinon\.mock|vi\.mock|vi\.spyOn|td\.replace)\s*\(',
    re.IGNORECASE
)

_INTERNAL_NAMES = re.compile(
    r'\b(?:validate|calculate|process|format|parse|helper|util|transform|convert|normalize|sanitize)\b',
    re.IGNORECASE
)

_RELATIVE_IMPORT_MOCK = re.compile(
    r'''(?:jest\.mock|vi\.mock)\s*\(\s*['"]\./'''
)


class MockBoundariesScanner(JSCodeScanner):
    """Detects mocking of internal code — mocks should target external boundaries only."""

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

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if not _MOCK_CALL.search(line):
                continue

            if _INTERNAL_NAMES.search(line):
                func_match = _INTERNAL_NAMES.search(line)
                word = func_match.group(0) if func_match else 'internal'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Mock targets internal function "{word}". '
                        'Only mock external boundaries (APIs, databases, file system, third-party services).'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='warning'
                ).to_dict())
                continue

            if _RELATIVE_IMPORT_MOCK.search(line):
                mod_match = re.search(r'''['"](\.\/[^'"]+)['"]''', line)
                mod_name = mod_match.group(1) if mod_match else 'relative module'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'jest.mock/vi.mock targets relative module "{mod_name}". '
                        'Prefer mocking external boundaries; call internal code directly.'
                    ),
                    location=str(file_path),
                    line_number=line_num,
                    severity='warning'
                ).to_dict())

        return violations
