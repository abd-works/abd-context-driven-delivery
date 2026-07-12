"""Scanner: detect functions exceeding 20 lines."""
import ast
from pathlib import Path
from code_scanner import CodeScanner


class FunctionSizeScanner(CodeScanner):

    MAX_LINES = 20


    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            result = self._read_and_parse_file(file_path)
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    size = self._function_line_count(node)
                    if size > self.MAX_LINES:
                        violations.append(self.violation(
                            f"Function '{node.name}' is {size} lines "
                            f"(max {self.MAX_LINES}). Extract helpers.",
                            location=str(file_path),
                            line=node.lineno,
                        ))
        return violations


if __name__ == '__main__':
    from scanners import run_scanner_main
    from code_scanner import collect_python_files
    raise SystemExit(run_scanner_main(FunctionSizeScanner, 'keep-functions-small-focused', collect_python_files))
