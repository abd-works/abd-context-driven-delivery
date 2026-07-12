"""Scanner: detect hidden dependency construction in __init__."""
import ast
from pathlib import Path
from code_scanner import CodeScanner


class ExplicitDependenciesScanner(CodeScanner):


    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            result = self._read_and_parse_file(file_path)
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._check_class(node, file_path, violations)
        return violations

    def _check_class(self, class_node, file_path, violations):
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.Assign):
                        value = stmt.value
                        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
                            if value.func.id[0].isupper():
                                violations.append(self.violation(
                                    f"Hidden dependency '{value.func.id}()' constructed "
                                    f"inside __init__ in '{class_node.name}'. "
                                    "Inject via constructor parameter instead.",
                                    location=str(file_path),
                                    line=stmt.lineno,
                                ))


if __name__ == '__main__':
    from scanners import run_scanner_main
    from code_scanner import collect_python_files
    raise SystemExit(run_scanner_main(ExplicitDependenciesScanner, 'use-explicit-dependencies', collect_python_files))
