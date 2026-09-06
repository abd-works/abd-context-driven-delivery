"""Scanner: detect classes with too many public methods or mixed responsibilities."""
import ast
from pathlib import Path
from code_scanner import CodeScanner

IO_INDICATORS = {'open', 'read', 'write', 'print', 'send', 'recv', 'connect', 'execute', 'cursor'}
CALC_INDICATORS = {'sum', 'average', 'calculate', 'compute', 'total', 'score', 'convert', 'parse'}

MAX_PUBLIC_METHODS = 10


class SingleResponsibilityScanner(CodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in context.get('code_files', []):
            result = self._read_and_parse_file(Path(file_path))
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._check_class(node, file_path, violations)
        return violations

    def _check_class(self, class_node, file_path, violations):
        methods = [
            n for n in class_node.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        public = [m for m in methods if not m.name.startswith('_')]
        if len(public) > MAX_PUBLIC_METHODS:
            violations.append({
                'rule': self.rule,
                'message': (
                    f"Class '{class_node.name}' has {len(public)} public methods "
                    f"(max {MAX_PUBLIC_METHODS}). Split responsibilities."
                ),
                'location': str(file_path),
                'line': class_node.lineno,
            })
        has_io = False
        has_calc = False
        for method in methods:
            names = {n.attr if isinstance(n, ast.Attribute) else getattr(n, 'id', '')
                     for n in ast.walk(method)}
            names |= {method.name}
            lower_names = {n.lower() for n in names if isinstance(n, str)}
            if lower_names & IO_INDICATORS:
                has_io = True
            if lower_names & CALC_INDICATORS:
                has_calc = True
        if has_io and has_calc:
            violations.append({
                'rule': self.rule,
                'message': (
                    f"Class '{class_node.name}' mixes I/O and calculation methods. "
                    "Separate into distinct classes."
                ),
                'location': str(file_path),
                'line': class_node.lineno,
            })


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(SingleResponsibilityScanner, 'keep-classes-single-responsibility')
