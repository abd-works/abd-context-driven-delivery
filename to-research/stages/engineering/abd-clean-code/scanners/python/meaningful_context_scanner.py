"""Scanner: detect magic numbers and numbered variable names."""
import ast
import re
from pathlib import Path
from code_scanner import CodeScanner

WELL_KNOWN_MAGIC = {
    200, 201, 204, 301, 302, 400, 401, 403, 404, 405, 409, 422, 429, 500, 502, 503,
    60, 3600, 86400, 604800,
    1024, 2048, 4096, 8192,
}
SAFE_CONSTANTS = {0, 1, 2, -1, 0.0, 1.0, 0.5, 100, 10, True, False, None}
NUMBERED_VAR = re.compile(r'^[a-z]+\d+$')


class MeaningfulContextScanner(CodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in context.get('code_files', []):
            result = self._read_and_parse_file(Path(file_path))
            if result is None:
                continue
            content, lines, tree = result
            self._check_magic_numbers(tree, file_path, violations)
            self._check_numbered_names(tree, file_path, violations)
        return violations

    def _check_magic_numbers(self, tree, file_path, violations):
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if not isinstance(node.value, (int, float)):
                continue
            if node.value in SAFE_CONSTANTS:
                continue
            if node.value in WELL_KNOWN_MAGIC:
                violations.append({
                    'rule': self.rule,
                    'message': (
                        f"Magic number {node.value} used inline. "
                        "Extract to a named constant."
                    ),
                    'location': str(file_path),
                    'line': getattr(node, 'lineno', 0),
                })

    def _check_numbered_names(self, tree, file_path, violations):
        for node in ast.walk(tree):
            name = None
            if isinstance(node, ast.Name):
                name = node.id
            elif isinstance(node, ast.arg):
                name = node.arg
            if name and NUMBERED_VAR.match(name):
                violations.append({
                    'rule': self.rule,
                    'message': (
                        f"Numbered variable '{name}' lacks meaningful context. "
                        "Use a descriptive name."
                    ),
                    'location': str(file_path),
                    'line': getattr(node, 'lineno', 0),
                })


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(MeaningfulContextScanner, 'provide-meaningful-context')
