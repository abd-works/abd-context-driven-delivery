"""Scanner for design_api_through_failing_tests rule.

Checks that tests call real production APIs instead of using placeholder values.
Flags tests that assign literal placeholder strings ('TODO', 'placeholder', 'FIXME',
'stub', 'dummy', 'mock_value', 'fake') or have trivially-true assertions (assert True).
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext


class FailingTestApiScanner(TestScanner):

    PLACEHOLDER_PATTERNS = [
        r"['\"](?:TODO|FIXME|placeholder|stub|dummy|mock_value|fake|xxx|tbd)['\"]",
    ]

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        if not self._is_test_file(file_path):
            return self._empty_violation_list()

        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return self._empty_violation_list()

        content, lines, tree = parsed
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith('test_'):
                    violations.extend(
                        self._check_test_method(node, file_path, content, lines)
                    )

        return violations

    def _check_test_method(
        self, node: ast.FunctionDef, file_path: Path, content: str, lines: List[str]
    ) -> List[Dict[str, Any]]:
        violations = []

        start = node.lineno - 1
        end = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else start + 1
        test_body_text = '\n'.join(lines[start:end])

        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = list(re.finditer(pattern, test_body_text, re.IGNORECASE))
            for match in matches:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test "{node.name}" uses placeholder value "{match.group(0)}". '
                        f'Write tests against the REAL expected API. '
                        f'Call real constructors and methods even if they don\'t exist yet.'
                    ),
                    location=str(file_path),
                    line_number=node.lineno,
                    severity='warning'
                ).to_dict())

        violation = self._check_trivial_assertions(node, file_path)
        if violation:
            violations.append(violation)

        return violations

    def _check_trivial_assertions(
        self, node: ast.FunctionDef, file_path: Path
    ) -> Optional[Dict[str, Any]]:
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                if isinstance(child.test, ast.Constant) and child.test.value is True:
                    return Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Test "{node.name}" contains "assert True" which proves nothing. '
                            f'Tests must assert real expected behavior against real API calls.'
                        ),
                        location=str(file_path),
                        line_number=child.lineno if hasattr(child, 'lineno') else node.lineno,
                        severity='warning'
                    ).to_dict()
        return None
