"""Scanner: detect swallowed or bare exceptions."""
import ast
from pathlib import Path
from code_scanner import CodeScanner


class ExceptionHandlingScanner(CodeScanner):


    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            result = self._read_and_parse_file(file_path)
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
            violations.append(self.violation((
                    "Bare 'except:' catches all exceptions including SystemExit. "
                    "Use 'except SpecificError:'."
                ), location=str(file_path), line=handler.lineno))
        elif is_pass_only:
            violations.append(self.violation("Exception swallowed silently with 'pass'. Log or re-raise.", location=str(file_path), line=handler.lineno))


if __name__ == '__main__':
    from scanners import run_scanner_main
    from code_scanner import collect_python_files
    raise SystemExit(run_scanner_main(ExceptionHandlingScanner, 'use-exceptions-properly', collect_python_files))
