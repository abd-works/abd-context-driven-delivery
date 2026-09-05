"""Scanner for helper_extraction_and_reuse rule.

Checks that test files extract duplicate setup into reusable helpers.
Flags test classes where multiple test methods contain near-identical setup blocks
(same lines repeated across tests), indicating extraction opportunity.
"""

from typing import List, Dict, Any, Optional, Set, TYPE_CHECKING
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext


class HelperExtractionScanner(TestScanner):

    MIN_DUPLICATE_LINES = 3
    MIN_OCCURRENCES = 2

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
            if isinstance(node, ast.ClassDef):
                class_violations = self._check_class_for_duplicates(node, file_path, lines)
                violations.extend(class_violations)

        return violations

    def _check_class_for_duplicates(
        self, class_node: ast.ClassDef, file_path: Path, lines: List[str]
    ) -> List[Dict[str, Any]]:
        test_methods = [
            n for n in class_node.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name.startswith('test_')
        ]

        if len(test_methods) < self.MIN_OCCURRENCES:
            return []

        method_setup_blocks = []
        for method in test_methods:
            setup_lines = self._extract_setup_lines(method, lines)
            if setup_lines:
                method_setup_blocks.append((method, setup_lines))

        violations = []
        reported_blocks: Set[str] = set()

        for i, (method_a, setup_a) in enumerate(method_setup_blocks):
            for j in range(i + 1, len(method_setup_blocks)):
                method_b, setup_b = method_setup_blocks[j]
                common = self._find_common_lines(setup_a, setup_b)
                if len(common) >= self.MIN_DUPLICATE_LINES:
                    block_key = '\n'.join(sorted(common))
                    if block_key not in reported_blocks:
                        reported_blocks.add(block_key)
                        violations.append(Violation(
                            rule=self.rule,
                            violation_message=(
                                f'Class "{class_node.name}": tests "{method_a.name}" and '
                                f'"{method_b.name}" share {len(common)} duplicate setup lines. '
                                f'Extract to a reusable helper function.'
                            ),
                            location=str(file_path),
                            line_number=method_a.lineno,
                            severity='warning'
                        ).to_dict())

        return violations

    def _extract_setup_lines(
        self, method: ast.FunctionDef, lines: List[str]
    ) -> List[str]:
        start = method.lineno
        end = method.end_lineno if hasattr(method, 'end_lineno') and method.end_lineno else start + 1

        setup_lines = []
        for line in lines[start:end]:
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if stripped.startswith('assert ') or stripped.startswith('assert('):
                break
            setup_lines.append(stripped)

        return setup_lines

    def _find_common_lines(self, lines_a: List[str], lines_b: List[str]) -> List[str]:
        set_b = set(lines_b)
        return [line for line in lines_a if line in set_b]
