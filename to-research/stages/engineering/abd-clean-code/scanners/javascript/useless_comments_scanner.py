"""Scanner: detect comments that merely repeat the code they describe."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

SKIP_PREFIXES = re.compile(
    r'^\s*(?://|/\*|\*)\s*(?:TODO|FIXME|HACK|NOTE|XXX|copyright|license|eslint|@)',
    re.IGNORECASE,
)
USELESS_PATTERNS = [
    re.compile(r'//\s*function\s+\w+', re.IGNORECASE),
    re.compile(r'//\s*return\b', re.IGNORECASE),
    re.compile(r'//\s*end\s+of\b', re.IGNORECASE),
    re.compile(r'//\s*import\b', re.IGNORECASE),
    re.compile(r'//\s*export\b', re.IGNORECASE),
    re.compile(r'//\s*constructor\b', re.IGNORECASE),
    re.compile(r'//\s*set\s+\w+\s+to\b', re.IGNORECASE),
    re.compile(r'//\s*declare\b', re.IGNORECASE),
    re.compile(r'//\s*initialize\b', re.IGNORECASE),
    re.compile(r'//\s*increment\b', re.IGNORECASE),
    re.compile(r'//\s*decrement\b', re.IGNORECASE),
    re.compile(r'//\s*loop\s+(?:through|over)\b', re.IGNORECASE),
    re.compile(r'//\s*define\s+\w+', re.IGNORECASE),
    re.compile(r'//\s*create\s+(?:a\s+)?new\b', re.IGNORECASE),
    re.compile(r'//\s*assign\b', re.IGNORECASE),
]


class UselessCommentsScanner(JsCodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            for i, line in enumerate(content.split('\n')):
                stripped = line.strip()
                if not stripped or SKIP_PREFIXES.search(stripped):
                    continue
                for pat in USELESS_PATTERNS:
                    if pat.search(stripped):
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Comment repeats code: '{stripped[:60]}'. "
                                "Remove or explain non-obvious intent."
                            ),
                            'location': str(file_path),
                            'line': i + 1,
                        })
                        break
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(UselessCommentsScanner, 'stop-writing-useless-comments')
