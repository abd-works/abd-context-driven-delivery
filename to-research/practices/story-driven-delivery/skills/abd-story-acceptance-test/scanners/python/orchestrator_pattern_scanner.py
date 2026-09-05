"""Scanner for pytest_bdd_orchestrator_pattern rule.

Checks that test files use the orchestrator pattern:
- Test methods should be under 20 lines showing Given-When-Then flow.
- Test classes should be under 300 lines.
- No feature file step definitions (@given, @when, @then decorators).
- Helper functions should be under 20 lines.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext


class OrchestratorPatternScanner(TestScanner):

    MAX_TEST_METHOD_LINES = 20
    MAX_TEST_CLASS_LINES = 300
    MAX_HELPER_LINES = 20

    FEATURE_FILE_DECORATORS = {'given', 'when', 'then', 'step', 'scenario'}

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        if not self._is_test_file(file_path):
            return self._empty_violation_list()

        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return self._empty_violation_list()

        content, lines, tree = parsed
        violations = []

        violations.extend(self._check_feature_file_decorators(tree, file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                violation = self._check_class_size(node, file_path)
                if violation:
                    violations.append(violation)

                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if child.name.startswith('test_'):
                            violation = self._check_test_method_size(child, file_path)
                            if violation:
                                violations.append(violation)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('test_') and not node.name.startswith('_'):
                    violation = self._check_helper_size(node, file_path)
                    if violation:
                        violations.append(violation)

        return violations

    def _check_feature_file_decorators(
        self, tree: ast.AST, file_path: Path
    ) -> List[Dict[str, Any]]:
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    decorator_name = self._get_decorator_name(decorator)
                    if decorator_name and decorator_name.lower() in self.FEATURE_FILE_DECORATORS:
                        violations.append(Violation(
                            rule=self.rule,
                            violation_message=(
                                f'Function "{node.name}" uses @{decorator_name} decorator '
                                f'(feature file / step definition style). '
                                f'Use pytest orchestrator pattern instead: test methods call '
                                f'helper functions directly, no feature files.'
                            ),
                            location=str(file_path),
                            line_number=node.lineno,
                            severity='warning'
                        ).to_dict())
        return violations

    def _check_test_method_size(
        self, node: ast.FunctionDef, file_path: Path
    ) -> Optional[Dict[str, Any]]:
        method_lines = self._count_body_lines(node)
        if method_lines > self.MAX_TEST_METHOD_LINES:
            return Violation(
                rule=self.rule,
                violation_message=(
                    f'Test method "{node.name}" is {method_lines} lines '
                    f'(max {self.MAX_TEST_METHOD_LINES}). '
                    f'Orchestrator pattern: test shows Given-When-Then flow and '
                    f'delegates details to helper functions.'
                ),
                location=str(file_path),
                line_number=node.lineno,
                severity='warning'
            ).to_dict()
        return None

    def _check_class_size(
        self, node: ast.ClassDef, file_path: Path
    ) -> Optional[Dict[str, Any]]:
        if not hasattr(node, 'end_lineno') or not node.end_lineno:
            return None
        class_lines = node.end_lineno - node.lineno + 1
        if class_lines > self.MAX_TEST_CLASS_LINES:
            return Violation(
                rule=self.rule,
                violation_message=(
                    f'Test class "{node.name}" is {class_lines} lines '
                    f'(max {self.MAX_TEST_CLASS_LINES}). '
                    f'Extract shared setup to helpers and keep classes focused.'
                ),
                location=str(file_path),
                line_number=node.lineno,
                severity='warning'
            ).to_dict()
        return None

    def _check_helper_size(
        self, node: ast.FunctionDef, file_path: Path
    ) -> Optional[Dict[str, Any]]:
        helper_lines = self._count_body_lines(node)
        if helper_lines > self.MAX_HELPER_LINES:
            return Violation(
                rule=self.rule,
                violation_message=(
                    f'Helper function "{node.name}" is {helper_lines} lines '
                    f'(max {self.MAX_HELPER_LINES}). '
                    f'Keep helpers focused and under {self.MAX_HELPER_LINES} lines.'
                ),
                location=str(file_path),
                line_number=node.lineno,
                severity='warning'
            ).to_dict()
        return None

    def _count_body_lines(self, node: ast.FunctionDef) -> int:
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno - node.lineno
        return len(node.body)

    def _get_decorator_name(self, decorator) -> Optional[str]:
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return None
