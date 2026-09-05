"""Scanner: detect functions with too many or vaguely named parameters."""
import ast
from pathlib import Path
from code_scanner import CodeScanner

MAX_PARAMS = 5
MAX_INIT_PARAMS = 7
VAGUE_NAMES = {'thing', 'stuff', 'info', 'data', 'args_list', 'params', 'options', 'misc', 'obj', 'payload'}
SKIP_PARAMS = {'self', 'cls'}


class ClearParametersScanner(CodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in context.get('code_files', []):
            result = self._read_and_parse_file(Path(file_path))
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._check_params(node, file_path, violations)
        return violations

    def _check_params(self, func, file_path, violations):
        all_args = [a.arg for a in func.args.args if a.arg not in SKIP_PARAMS]
        limit = MAX_INIT_PARAMS if func.name == '__init__' else MAX_PARAMS
        if len(all_args) > limit:
            violations.append({
                'rule': self.rule,
                'message': (
                    f"Function '{func.name}' has {len(all_args)} parameters "
                    f"(max {limit}). Group related params into an object."
                ),
                'location': str(file_path),
                'line': func.lineno,
            })
        for arg_name in all_args:
            if arg_name.lower() in VAGUE_NAMES:
                violations.append({
                    'rule': self.rule,
                    'message': (
                        f"Parameter '{arg_name}' in '{func.name}' is vague. "
                        "Use a domain-specific name."
                    ),
                    'location': str(file_path),
                    'line': func.lineno,
                })


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(ClearParametersScanner, 'use-clear-function-parameters')
