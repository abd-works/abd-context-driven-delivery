"""Scanner for verifying test files call real production code, not just mocks."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

_IMPORT_LINE = re.compile(
    r'''^\s*(?:import\s+.*\s+from\s+['"](.*?)['"]|'''
    r'''(?:const|let|var)\s+.*=\s*require\s*\(\s*['"](.*?)['"]\s*\))''',
    re.MULTILINE
)

_TEST_INFRA_MODULES = {
    'jest', '@jest', 'mocha', 'chai', 'sinon', 'vitest',
    'supertest', '@testing-library', 'enzyme', 'nock',
    'jest-mock', 'ts-jest', 'faker', '@faker-js',
    'test-utils', 'testing', 'mock', 'stub', 'fixture',
}

_MOCK_ONLY_PATTERNS = re.compile(
    r'jest\.mock|jest\.spyOn|sinon\.stub|sinon\.mock|vi\.mock|vi\.spyOn|td\.replace',
    re.IGNORECASE
)

_PRODUCTION_CALL = re.compile(
    r'(?:new\s+[A-Z]\w+|(?:await\s+)?(?!expect|describe|it|test|before|after)\w+\.\w+\s*\()',
)


class RealImplementationsScanner(JSCodeScanner):
    """Checks that test files import and call real production modules, not just test infra."""

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

        imports = _IMPORT_LINE.findall(content)
        prod_imports = []
        infra_imports = []

        for groups in imports:
            module = groups[0] or groups[1]
            if not module:
                continue
            if self._is_test_infra(module):
                infra_imports.append(module)
            else:
                prod_imports.append(module)

        if not prod_imports and infra_imports:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    'Test file imports only test infrastructure — no production module imports found. '
                    'Tests should import and call real production code directly.'
                ),
                location=str(file_path),
                line_number=1,
                severity='warning'
            ).to_dict())

        mock_count = len(_MOCK_ONLY_PATTERNS.findall(content))
        if mock_count > 0 and not prod_imports:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    f'Test file has {mock_count} mock setup(s) but no production imports. '
                    'Call production code directly; only mock external boundaries.'
                ),
                location=str(file_path),
                line_number=1,
                severity='warning'
            ).to_dict())

        return violations

    def _is_test_infra(self, module: str) -> bool:
        mod_lower = module.lower()
        base = mod_lower.split('/')[0]
        if base in _TEST_INFRA_MODULES:
            return True
        return any(kw in mod_lower for kw in ('mock', 'stub', 'fixture', 'fake', '__mocks__'))

    def _is_test_file(self, path_str: str) -> bool:
        return any(marker in path_str for marker in (
            '.test.', '.spec.', '__tests__', '/test/', '\\test\\'
        ))
