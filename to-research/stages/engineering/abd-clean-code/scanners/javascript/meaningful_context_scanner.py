"""Scanner: detect magic numbers and numbered variable names."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

MAGIC_NUMBERS = re.compile(
    r'(?<![.\w])\b(200|201|204|301|302|400|401|403|404|500|502|503|'
    r'86400|3600|1000|60000|1024|2048|4096)\b(?!\s*[;,\]})]\s*//)'
)
CONST_CONTEXT = re.compile(
    r'(?:const|let|var|#?\w+\s*[:=])\s*.*\b\d+\b'
)
ALLOWED_LINE = re.compile(
    r'^\s*(?:const|let|var|export\s+const|static)\s+[A-Z_]+\s*='
)
NUMBERED_VAR = re.compile(
    r'\b(?:const|let|var)\s+(\w+[0-9]+)\b'
)
SIMPLE_NUMBERS = {'0', '1', '2', '-1'}


class MeaningfulContextScanner(JsCodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            for i, line in enumerate(content.split('\n')):
                stripped = line.strip()
                if ALLOWED_LINE.match(stripped):
                    continue
                match = MAGIC_NUMBERS.search(stripped)
                if match:
                    num = match.group(1)
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Magic number {num} used inline. "
                            "Extract to a named constant."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
                nv = NUMBERED_VAR.search(stripped)
                if nv:
                    var_name = nv.group(1)
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Numbered variable '{var_name}' lacks meaningful context. "
                            "Use a descriptive name."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(MeaningfulContextScanner, 'provide-meaningful-context')
