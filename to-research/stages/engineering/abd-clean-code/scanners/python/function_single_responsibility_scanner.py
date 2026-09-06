"""Scanner: detect functions mixing logging/print with computation, or validation with processing."""
import ast
from pathlib import Path
from code_scanner import CodeScanner

LOG_CALLS = {'print', 'pprint'}
LOG_ATTRS = {'debug', 'info', 'warning', 'error', 'critical', 'exception', 'log'}
VALIDATION_PATTERNS = {'validate', 'check', 'verify', 'assert', 'ensure'}
IO_CALLS = {'open', 'read', 'write'}
IO_ATTRS = {'read', 'write', 'readline', 'readlines', 'send', 'recv', 'get', 'post', 'put', 'delete'}


class FunctionSingleResponsibilityScanner(CodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in context.get('code_files', []):
            result = self._read_and_parse_file(Path(file_path))
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._check_function(node, file_path, violations)
        return violations

    def _check_function(self, func, file_path, violations):
        has_log = False
        has_calc = False
        has_validation = False
        has_io = False

        for child in ast.walk(func):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    name = child.func.id
                    if name in LOG_CALLS:
                        has_log = True
                    if name in IO_CALLS:
                        has_io = True
                elif isinstance(child.func, ast.Attribute):
                    attr = child.func.attr
                    if attr in LOG_ATTRS:
                        has_log = True
                    if attr in IO_ATTRS:
                        has_io = True
                    if any(attr.startswith(v) for v in VALIDATION_PATTERNS):
                        has_validation = True
            if isinstance(child, (ast.BinOp, ast.ListComp, ast.DictComp, ast.SetComp)):
                has_calc = True
            if isinstance(child, ast.If) and isinstance(child.test, ast.Compare):
                for stmt in child.body:
                    if isinstance(stmt, ast.Raise):
                        has_validation = True

        if has_log and has_calc:
            violations.append({
                'rule': self.rule,
                'message': (
                    f"Function '{func.name}' mixes logging with computation. "
                    "Separate the pure logic from observability concerns."
                ),
                'location': str(file_path),
                'line': func.lineno,
            })
        if has_validation and has_io:
            violations.append({
                'rule': self.rule,
                'message': (
                    f"Function '{func.name}' mixes validation with I/O. "
                    "Validate in a separate function."
                ),
                'location': str(file_path),
                'line': func.lineno,
            })


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(FunctionSingleResponsibilityScanner, 'keep-functions-single-responsibility')
