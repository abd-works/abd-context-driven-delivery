"""Scanner for call-production-code-directly rule.

Checks that test files import and call real production code.
Flags: (a) test methods with no production code imports,
(b) empty/TODO-only test methods, (c) fake/stub implementations.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

STDLIB_AND_TEST_MODULES = {
    'pytest', 'unittest', 'mock', 'pathlib', 'json', 'typing', 'os', 'sys',
    'collections', 'dataclasses', 'enum', 'abc', 'logging', 'datetime',
    'time', 're', 'random', 'math', 'itertools', 'functools', 'copy',
    'io', 'tempfile', 'shutil', 'textwrap', 'pprint', 'contextlib',
}

FAKE_PATTERNS = [
    re.compile(r'\bfake_\w+\s*=', re.IGNORECASE),
    re.compile(r'\bstub_\w+\s*=', re.IGNORECASE),
    re.compile(r'\w+\s*=\s*Mock\(', re.IGNORECASE),
    re.compile(r'return\s+\{\s*\}'),
]


class RealImplementationsScanner(TestScanner):

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        violations = []

        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations

        content, lines, tree = parsed

        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        has_prod_import = self._has_production_imports(imports)
        test_methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]

        if test_methods and not has_prod_import:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    'Test file has no production code imports. '
                    'Tests must import real production modules (not just pytest/pathlib/json). '
                    'If production code does not exist yet, the import should fail with ImportError.'
                ),
                location=str(file_path),
                line_number=1,
                severity='error'
            ).to_dict())

        for method in test_methods:
            if self._is_empty_or_todo(method, lines):
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test method "{method.name}" (line {method.lineno}) is empty or TODO-only. '
                        f'Tests must call production code directly.'
                    ),
                    location=str(file_path),
                    line_number=method.lineno,
                    severity='error'
                ).to_dict())

        violations.extend(self._check_fake_implementations(lines, file_path))
        return violations

    def _has_production_imports(self, imports: list) -> bool:
        for imp in imports:
            if isinstance(imp, ast.ImportFrom):
                module = (imp.module or '').split('.')[0]
                if module and module not in STDLIB_AND_TEST_MODULES and 'test' not in module.lower():
                    return True
            elif isinstance(imp, ast.Import):
                for alias in imp.names:
                    top = alias.name.split('.')[0]
                    if top not in STDLIB_AND_TEST_MODULES and 'test' not in top.lower():
                        return True
        return False

    def _is_empty_or_todo(self, method: ast.FunctionDef, lines: List[str]) -> bool:
        if not method.body:
            return True
        start = method.lineno - 1
        end = getattr(method, 'end_lineno', start + 1)
        body_text = '\n'.join(lines[start:end])
        if 'TODO' in body_text or 'FIXME' in body_text:
            return True
        for stmt in method.body:
            if isinstance(stmt, ast.Pass):
                continue
            if isinstance(stmt, ast.Expr) and isinstance(getattr(stmt, 'value', None), ast.Constant):
                if isinstance(stmt.value.value, str):
                    continue
            return False
        return True

    def _check_fake_implementations(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        for line_num, line in enumerate(lines, 1):
            for pattern in FAKE_PATTERNS:
                if pattern.search(line):
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Line {line_num} uses fake/stub implementation — '
                            f'tests should call real production code directly'
                        ),
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict())
                    break
        return violations
