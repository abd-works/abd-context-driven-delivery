"""Scanner: detect swallowed or bare exceptions."""
import ast
from pathlib import Path
from code_scanner import CodeScanner


class ExceptionHandlingScanner(CodeScanner):

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
        is_bare = handler.type is None
        is_pass_only = (
            len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass)
        )
        if is_bare:
            violations.append({
                'rule': self.rule,
                'message': (
                    "Bare 'except:' catches all exceptions including SystemExit. "
                    "Use 'except SpecificError:'."
                ),
                'location': str(file_path),
                'line': handler.lineno,
            })
        elif is_pass_only:
            violations.append({
                'rule': self.rule,
                'message': "Exception swallowed silently with 'pass'. Log or re-raise.",
                'location': str(file_path),
                'line': handler.lineno,
            })


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(ExceptionHandlingScanner, 'use-exceptions-properly')
