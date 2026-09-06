"""Scanner for bug_fix_test_first rule.

Checks that test files contain bug-reproducing tests with proper RED-GREEN workflow
indicators: comments referencing bug reproduction, failure verification, or fix verification.
Flags test methods named with bug/fix/regression patterns that lack reproduction comments.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext


class BugFixTestFirstScanner(TestScanner):

    BUG_FIX_NAME_PATTERNS = [
        r'test_.*(?:bug|fix|regression|broken|issue|patch|hotfix)',
        r'test_(?:fix|repair|resolve|correct)_',
    ]

    REPRODUCTION_INDICATORS = [
        r'#\s*(?:reproduces?|bug|fix|regression|issue|broken|red|green)',
        r'(?:reproduces?|bug\s*fix|regression\s*test)',
        r'#\s*(?:expected|should)\s*(?:fail|raise|error)',
        r'#\s*(?:run|verify|confirm)\s*.*(?:fail|pass|red|green)',
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
                    violation = self._check_bug_fix_test(node, file_path, content, lines)
                    if violation:
                        violations.append(violation)

        return violations

    def _check_bug_fix_test(
        self, node: ast.FunctionDef, file_path: Path, content: str, lines: List[str]
    ) -> Optional[Dict[str, Any]]:
        is_bug_fix_test = any(
            re.search(pattern, node.name, re.IGNORECASE)
            for pattern in self.BUG_FIX_NAME_PATTERNS
        )
        if not is_bug_fix_test:
            return None

        start = node.lineno - 1
        end = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else start + 1
        test_body_lines = lines[start:end]
        test_body_text = '\n'.join(test_body_lines)

        has_reproduction = any(
            re.search(indicator, test_body_text, re.IGNORECASE)
            for indicator in self.REPRODUCTION_INDICATORS
        )

        if not has_reproduction:
            return Violation(
                rule=self.rule,
                violation_message=(
                    f'Bug-fix test "{node.name}" lacks reproduction comments. '
                    f'Follow RED-GREEN workflow: add a comment explaining which bug this '
                    f'reproduces and verify test fails before fix (RED) then passes after (GREEN).'
                ),
                location=str(file_path),
                line_number=node.lineno,
                severity='warning'
            ).to_dict()

        return None
