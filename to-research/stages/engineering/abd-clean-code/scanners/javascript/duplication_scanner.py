"""Scanner: detect likely-duplicate functions via signature and body hashing."""
import re
import hashlib
from pathlib import Path
from js_code_scanner import JsCodeScanner

FUNC_PATTERN = re.compile(
    r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
)
WHITESPACE = re.compile(r'\s+')


class DuplicationScanner(JsCodeScanner):

    MIN_LINES = 5

    def scan(self, context) -> list:
        violations = []
        seen = {}
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines):
                match = FUNC_PATTERN.search(line)
                if not match:
                    continue
                func_name = match.group(1) or match.group(2) or '<anonymous>'
                size = self._count_function_lines(content, i)
                if size < self.MIN_LINES:
                    continue
                body = '\n'.join(lines[i + 1:i + size])
                normalized = WHITESPACE.sub(' ', body).strip()
                digest = hashlib.md5(normalized.encode()).hexdigest()
                key = digest
                if key in seen:
                    orig_name, orig_file, orig_line = seen[key]
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Function '{func_name}' appears to duplicate "
                            f"'{orig_name}' ({orig_file}:{orig_line}). "
                            "Extract a shared helper."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
                else:
                    seen[key] = (func_name, str(file_path), i + 1)
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(DuplicationScanner, 'eliminate-duplication')
