"""Scanner: detect mixed naming conventions (snake_case vs camelCase) in a file."""
import ast
import re
from pathlib import Path
from code_scanner import CodeScanner

SNAKE_CASE = re.compile(r'^_*[a-z][a-z0-9]*(_[a-z0-9]+)*_*$')
CAMEL_CASE = re.compile(r'^_*[a-z]+[A-Z][a-zA-Z0-9]*$')
DUNDER = re.compile(r'^__[a-z]+__$')
SKIP_NAMES = {'setUp', 'tearDown', 'setUpClass', 'tearDownClass', 'setUpModule'}


class ConsistentNamingScanner(CodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in context.get('code_files', []):
            result = self._read_and_parse_file(Path(file_path))
            if result is None:
                continue
            content, lines, tree = result
            snake_funcs = []
            camel_funcs = []
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                name = node.name
                if name in SKIP_NAMES or DUNDER.match(name):
                    continue
                if CAMEL_CASE.match(name):
                    camel_funcs.append(node)
                elif SNAKE_CASE.match(name):
                    snake_funcs.append(node)
            if snake_funcs and camel_funcs:
                minority = camel_funcs if len(camel_funcs) <= len(snake_funcs) else snake_funcs
                style = 'camelCase' if minority is camel_funcs else 'snake_case'
                for node in minority:
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Function '{node.name}' uses {style} while the file "
                            "majority uses the other convention. Be consistent."
                        ),
                        'location': str(file_path),
                        'line': node.lineno,
                    })
        return violations


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(ConsistentNamingScanner, 'use-consistent-naming')
