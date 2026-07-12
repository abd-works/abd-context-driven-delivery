"""Scanner: detect encapsulation violations — public fields, leaked mutables, missing @property."""
import ast
from pathlib import Path
from code_scanner import CodeScanner

MUTABLE_CONSTRUCTORS = {'list', 'dict', 'set', 'defaultdict', 'OrderedDict'}
PROPERTY_PREFIXES = ('calculate_', 'compute_', 'get_')


class PropertyEncapsulationCodeScanner(CodeScanner):


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
        property_names = {
            n.name for n in class_node.body
            if isinstance(n, ast.FunctionDef)
            and any(
                isinstance(d, ast.Name) and d.id == 'property'
                for d in n.decorator_list
            )
        }
        for item in class_node.body:
            if not (isinstance(item, ast.FunctionDef) and item.name == '__init__'):
                continue
            for stmt in ast.walk(item):
                if not isinstance(stmt, ast.Assign):
                    continue
                for target in stmt.targets:
                    if not (isinstance(target, ast.Attribute) and
                            isinstance(target.value, ast.Name) and
                            target.value.id == 'self'):
                        continue
                    attr = target.attr
                    if not attr.startswith('_'):
                        violations.append(self.violation((
                                f"Public attribute 'self.{attr}' in '{class_node.name}.__init__'. "
                                "Prefix with '_' and expose via @property."
                            ), location=str(file_path), line=stmt.lineno))

        for method in class_node.body:
            if not isinstance(method, ast.FunctionDef):
                continue
            if method.name in property_names:
                continue
            if any(method.name.startswith(p) for p in PROPERTY_PREFIXES):
                if len(method.args.args) == 1:
                    violations.append(self.violation((
                            f"Method '{method.name}' in '{class_node.name}' takes no args "
                            "beyond self — use @property."
                        ), location=str(file_path), line=method.lineno))

            for stmt in ast.walk(method):
                if not isinstance(stmt, ast.Return) or stmt.value is None:
                    continue
                val = stmt.value
                if isinstance(val, ast.Attribute) and isinstance(val.value, ast.Name):
                    if val.value.id == 'self' and val.attr.startswith('_'):
                        violations.append(self.violation((
                                f"Method '{method.name}' returns mutable internal "
                                f"'self.{val.attr}' directly. Return a copy."
                            ), location=str(file_path), line=stmt.lineno))


if __name__ == '__main__':
    from scanners import run_scanner_main
    from code_scanner import collect_python_files
    raise SystemExit(run_scanner_main(PropertyEncapsulationCodeScanner, 'enforce-encapsulation', collect_python_files))
