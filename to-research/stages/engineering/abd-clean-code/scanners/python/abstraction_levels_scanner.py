"""Scanner: detect functions mixing high-level orchestration with low-level I/O."""
import ast
from pathlib import Path
from code_scanner import CodeScanner

HIGH_LEVEL_NAMES = {'orchestrate', 'coordinate', 'process', 'handle', 'dispatch', 'workflow', 'pipeline'}
LOW_LEVEL_CALLS = {'open', 'read', 'write', 'cursor', 'execute', 'connect', 'socket', 'recv', 'send'}
LOW_LEVEL_ATTRS = {'read_text', 'write_text', 'read_bytes', 'write_bytes', 'executemany', 'fetchone', 'fetchall'}
SQL_STRINGS = {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE', 'DROP'}


class AbstractionLevelsScanner(CodeScanner):

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
        is_high = any(kw in func.name.lower() for kw in HIGH_LEVEL_NAMES)
        if not is_high:
            return
        has_low = False
        for child in ast.walk(func):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id in LOW_LEVEL_CALLS:
                    has_low = True
                elif isinstance(child.func, ast.Attribute) and child.func.attr in LOW_LEVEL_ATTRS:
                    has_low = True
            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                upper = child.value.upper().lstrip()
                if any(upper.startswith(kw) for kw in SQL_STRINGS):
                    has_low = True
        if has_low:
            violations.append({
                'rule': self.rule,
                'message': (
                    f"Function '{func.name}' mixes high-level orchestration with "
                    "low-level I/O. Delegate I/O to a separate function."
                ),
                'location': str(file_path),
                'line': func.lineno,
            })


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(AbstractionLevelsScanner, 'maintain-abstraction-levels')
