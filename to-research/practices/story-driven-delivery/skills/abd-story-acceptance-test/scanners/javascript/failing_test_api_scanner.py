"""Scanner for failing-test API surface in JavaScript/TypeScript.

Checks that test files exercise real API surface by importing production
modules. Flags test files with no production imports or only
test-infrastructure imports.
"""

import re
from typing import List, Dict, Any, Set, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

IMPORT_RE = re.compile(
    r'''(?:import\s+.*?\s+from\s+['"](.+?)['"]|'''
    r'''require\s*\(\s*['"](.+?)['"]\s*\))''',
    re.MULTILINE,
)
TEST_INFRA_MODULES: Set[str] = {
    'jest', 'mocha', 'chai', 'sinon', 'jasmine', 'vitest',
    'supertest', 'nock', 'assert', 'expect', '@jest/globals',
    'testing-library', '@testing-library', 'enzyme',
    'test-utils', 'ts-jest', 'jest-mock',
}
TEST_FILE_RE = re.compile(
    r'(?:\.test\.|\.spec\.|__tests__|test_)', re.IGNORECASE
)


class FailingTestApiScanner(JSCodeScanner):

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')):
            return violations
        if not TEST_FILE_RE.search(path_str):
            return violations
        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations

        imports = []
        for m in IMPORT_RE.finditer(content):
            module = m.group(1) or m.group(2)
            if module:
                imports.append(module)

        if not imports:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    'Test file has no import/require statements. '
                    'Tests must import production modules to exercise their API.'
                ),
                location=str(file_path),
                line_number=1,
                severity='error'
            ).to_dict())
            return violations

        has_production = False
        for mod in imports:
            mod_lower = mod.lower()
            if mod.startswith('.'):
                has_production = True
                break
            is_infra = any(infra in mod_lower for infra in TEST_INFRA_MODULES)
            if not is_infra:
                has_production = True
                break

        if not has_production:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    'Test file only imports test infrastructure — no production '
                    'modules found. Tests must import and call real production code.'
                ),
                location=str(file_path),
                line_number=1,
                severity='error'
            ).to_dict())
        return violations
