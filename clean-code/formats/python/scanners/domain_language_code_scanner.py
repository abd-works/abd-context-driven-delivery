"""Scanner: detect generic class and method names that lack domain language."""
import ast
from pathlib import Path
from code_scanner import CodeScanner

GENERIC_CLASS_NAMES = {
    'Manager', 'Handler', 'Helper', 'Util', 'Utils',
    'Processor', 'Service', 'Controller', 'Base',
}
GENERIC_METHOD_NAMES = {
    'process', 'handle', 'execute', 'run', 'do', 'perform', 'manage',
}


class DomainLanguageCodeScanner(CodeScanner):


    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            result = self._read_and_parse_file(file_path)
            if result is None:
                continue
            content, lines, tree = result
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name in GENERIC_CLASS_NAMES:
                        violations.append(self.violation((
                                f"Class '{node.name}' is a generic name. "
                                "Use a domain entity name instead."
                            ), location=str(file_path), line=node.lineno))
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name in GENERIC_METHOD_NAMES:
                        violations.append(self.violation((
                                f"Method '{node.name}' is too generic. "
                                "Use a domain responsibility verb."
                            ), location=str(file_path), line=node.lineno))
        return violations


if __name__ == '__main__':
    from scanners import run_scanner_main
    from code_scanner import collect_python_files
    raise SystemExit(run_scanner_main(DomainLanguageCodeScanner, 'use-domain-language', collect_python_files))
