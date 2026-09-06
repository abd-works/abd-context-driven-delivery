"""Scanner: detect duplicate function bodies via normalized AST hashing."""
import ast
import hashlib
from pathlib import Path
from code_scanner import CodeScanner

MIN_BODY_STATEMENTS = 3


class DuplicationScanner(CodeScanner):

    def scan(self, context) -> list:
        violations = []
        seen = {}
        for file_path in context.get('code_files', []):
            result = self._read_and_parse_file(Path(file_path))
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if len(node.body) < MIN_BODY_STATEMENTS:
                        continue
                    body_hash = self._hash_body(node)
                    key = body_hash
                    if key in seen:
                        orig_name, orig_file, orig_line = seen[key]
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Function '{node.name}' has the same body as "
                                f"'{orig_name}' ({orig_file}:{orig_line}). "
                                "Extract shared logic."
                            ),
                            'location': str(file_path),
                            'line': node.lineno,
                        })
                    else:
                        seen[key] = (node.name, str(file_path), node.lineno)
        return violations

    def _hash_body(self, func_node) -> str:
        normalized = ast.dump(ast.Module(body=func_node.body, type_ignores=[]))
        return hashlib.sha256(normalized.encode()).hexdigest()


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(DuplicationScanner, 'eliminate-duplication')
