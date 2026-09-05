"""Scanner: detect functions mixing DOM manipulation with business logic or I/O with computation."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

FUNC_PATTERN = re.compile(
    r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
)
DOM_PATTERNS = re.compile(
    r'\b(?:document\.\w+|\.innerHTML|\.textContent|\.classList\.|'
    r'\.appendChild|\.removeChild|\.setAttribute|\.getElementById|'
    r'\.querySelector|\.querySelectorAll|\.addEventListener)',
)
IO_PATTERNS = re.compile(
    r'\b(?:fetch\s*\(|axios\.|fs\.\w+|readFile|writeFile|'
    r'XMLHttpRequest|\.json\s*\()',
)
COMPUTATION_PATTERNS = re.compile(
    r'\b(?:Math\.\w+|\.map\s*\(|\.filter\s*\(|\.reduce\s*\(|'
    r'\.sort\s*\(|\.find\s*\(|return\s+)',
)


class SeparateConcernsScanner(JsCodeScanner):

    def scan(self, context) -> list:
        violations = []
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
                body = '\n'.join(lines[i:i + size])
                has_dom = bool(DOM_PATTERNS.search(body))
                has_io = bool(IO_PATTERNS.search(body))
                has_compute = bool(COMPUTATION_PATTERNS.search(body))
                if has_dom and has_compute:
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Function '{func_name}' mixes DOM manipulation with "
                            "computation. Separate view updates from business logic."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
                elif has_io and has_compute:
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Function '{func_name}' mixes I/O (fetch/fs) with "
                            "pure computation. Extract I/O into its own function."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(SeparateConcernsScanner, 'separate-concerns')
