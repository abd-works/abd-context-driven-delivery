"""Scanner: detect deep nesting that should use guard clauses or early returns."""
import ast
from pathlib import Path
from code_scanner import CodeScanner

MAX_NESTING = 3
NESTING_TYPES = (ast.If, ast.For, ast.While, ast.AsyncFor, ast.Try, ast.With, ast.AsyncWith)


class SimplifyControlFlowScanner(CodeScanner):


    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            result = self._read_and_parse_file(file_path)
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._check_depth(node, file_path, violations)
        return violations

    def _check_depth(self, func, file_path, violations):
        max_found = self._max_nesting(func.body, 0)
        if max_found > MAX_NESTING:
            violations.append(self.violation(
                f"Function '{func.name}' has nesting depth {max_found} "
                f"(max {MAX_NESTING}). Use guard clauses or early returns.",
                location=str(file_path),
                line=func.lineno,
            ))

    def _max_nesting(self, body, depth) -> int:
        deepest = depth
        for node in body:
            if isinstance(node, NESTING_TYPES):
                child_depth = depth + 1
                for field_name in ('body', 'orelse', 'handlers', 'finalbody'):
                    children = getattr(node, field_name, None)
                    if children:
                        deepest = max(deepest, self._max_nesting(children, child_depth))
            elif hasattr(node, 'body') and isinstance(node.body, list):
                deepest = max(deepest, self._max_nesting(node.body, depth))
        return deepest


if __name__ == '__main__':
    from scanners import run_scanner_main
    from code_scanner import collect_python_files
    raise SystemExit(run_scanner_main(SimplifyControlFlowScanner, 'simplify-control-flow', collect_python_files))
