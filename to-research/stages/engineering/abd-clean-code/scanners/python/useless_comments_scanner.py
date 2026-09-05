"""Scanner: detect comments that repeat code instead of explaining why."""
import ast
import re
from pathlib import Path
from code_scanner import CodeScanner

NARRATION_PATTERNS = re.compile(
    r'^\s*#\s*(get|set|return|handle|create|init|import|increment|decrement|define|declare)\s',
    re.IGNORECASE,
)
COMMENTED_CODE_PATTERN = re.compile(
    r'^\s*#\s*(def |class |import |from |if |for |while |return |raise |try:)',
)
USEFUL_PREFIXES = re.compile(
    r'^\s*#\s*(TODO|FIXME|HACK|NOTE|XXX|BUG|WARN|WHY|REASON|LEGAL|LICENSE|COPYRIGHT|type:\s*ignore|noqa)',
    re.IGNORECASE,
)


class UselessCommentsScanner(CodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in context.get('code_files', []):
            result = self._read_and_parse_file(Path(file_path))
            if result is None:
                continue
            content, lines, tree = result
            self._check_inline_comments(lines, file_path, violations)
            self._check_parrot_docstrings(tree, file_path, violations)
        return violations

    def _check_inline_comments(self, lines, file_path, violations):
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped.startswith('#'):
                continue
            if USEFUL_PREFIXES.match(stripped):
                continue
            if NARRATION_PATTERNS.match(stripped):
                violations.append({
                    'rule': self.rule,
                    'message': f"Comment narrates code instead of explaining why: '{stripped[:60]}'",
                    'location': str(file_path),
                    'line': i,
                })
            elif COMMENTED_CODE_PATTERN.match(stripped):
                violations.append({
                    'rule': self.rule,
                    'message': "Commented-out code detected. Remove or use version control.",
                    'location': str(file_path),
                    'line': i,
                })

    def _check_parrot_docstrings(self, tree, file_path, violations):
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            docstring = ast.get_docstring(node)
            if not docstring:
                continue
            name_words = set(node.name.lower().replace('_', ' ').split())
            doc_words = set(docstring.lower().strip('.').split())
            if name_words and doc_words and doc_words <= name_words:
                violations.append({
                    'rule': self.rule,
                    'message': f"Docstring for '{node.name}' just repeats its name.",
                    'location': str(file_path),
                    'line': node.lineno,
                })


if __name__ == '__main__':
    from code_scanner import run_scanner_main
    run_scanner_main(UselessCommentsScanner, 'stop-writing-useless-comments')
