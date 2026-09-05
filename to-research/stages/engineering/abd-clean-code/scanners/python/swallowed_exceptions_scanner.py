"""Scanner: detect swallowed exceptions and bare except handlers."""
import ast
from pathlib import Path
from code_scanner import CodeScanner


class SwallowedExceptionsScanner(CodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in context.get('code_files', []):
            result = self._read_and_parse_file(Path(file_path))
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    self._check_handler(node, file_path, violations)
        return violations

    def _check_handler(self, handler, file_path, violations):
        if handler.type is None:
            violations.append({
                'rule': self.rule,
                'message': (
                    "Bare 'except:' catches everything including SystemExit and "
                    "KeyboardInterrupt. Specify the exception type."
                ),
                'location': str(file_path),
                'line': handler.lineno,
            })
        body = handler.body
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            violations.append({
                'rule': self.rule,
                'message': "Exception swallowed with 'pass'. Log, re-raise, or handle it.",
                'location': str(file_path),
                'line': handler.lineno,
            })
        elif len(body) == 1 and isinstance(body[0], ast.Expr):
            if isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                violations.append({
                    'rule': self.rule,
                    'message': "Exception handler body is just a string literal (no effect). Handle the error.",
                    'location': str(file_path),
                    'line': handler.lineno,
                })


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(SwallowedExceptionsScanner, 'never-swallow-exceptions')
