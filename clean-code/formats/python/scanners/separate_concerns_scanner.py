"""Scanner: detect functions mixing I/O side effects with pure computation."""
import ast
from pathlib import Path
from code_scanner import CodeScanner

IO_CALLS = {'open', 'print', 'input'}
IO_ATTRS = {
    'read', 'write', 'readline', 'readlines', 'writelines', 'close', 'flush',
    'get', 'post', 'put', 'delete', 'patch', 'send', 'recv',
    'read_text', 'write_text', 'read_bytes', 'write_bytes',
}
CALC_OPS = (ast.BinOp, ast.BoolOp, ast.Compare, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


class SeparateConcernsScanner(CodeScanner):


    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            result = self._read_and_parse_file(file_path)
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._check_function(node, file_path, violations)
        return violations

    def _check_function(self, func, file_path, violations):
        has_io = False
        has_calc = False
        for child in ast.walk(func):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id in IO_CALLS:
                    has_io = True
                elif isinstance(child.func, ast.Attribute) and child.func.attr in IO_ATTRS:
                    has_io = True
            if isinstance(child, CALC_OPS):
                has_calc = True
        if has_io and has_calc:
            violations.append(self.violation((
                    f"Function '{func.name}' mixes I/O with computation. "
                    "Split into a pure function and an I/O wrapper."
                ), location=str(file_path), line=func.lineno))


if __name__ == '__main__':
    from scanners import run_scanner_main
    from code_scanner import collect_python_files
    raise SystemExit(run_scanner_main(SeparateConcernsScanner, 'separate-concerns', collect_python_files))
