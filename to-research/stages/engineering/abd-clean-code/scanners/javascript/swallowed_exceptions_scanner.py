"""Scanner: detect swallowed exceptions — empty catch or catch with only console.log."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

CATCH_PATTERN = re.compile(r'\bcatch\s*\(?\w*\)?\s*\{')
CONSOLE_ONLY = re.compile(r'^\s*console\.\w+\(')


class SwallowedExceptionsScanner(JsCodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if not CATCH_PATTERN.search(line):
                    continue
                body_lines = self._extract_catch_body(lines, i)
                if not body_lines:
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            "Empty catch block swallows exception silently. "
                            "Log, re-throw, or handle the error."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
                elif all(CONSOLE_ONLY.match(bl) for bl in body_lines):
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            "Catch block only logs the error. "
                            "Add recovery logic or re-throw with context."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
        return violations

    @staticmethod
    def _extract_catch_body(lines, catch_line):
        depth = 0
        body = []
        started = False
        for j in range(catch_line, min(catch_line + 30, len(lines))):
            depth += lines[j].count('{') - lines[j].count('}')
            if '{' in lines[j]:
                started = True
                first_after = lines[j].split('{', 1)[1].strip()
                if first_after and first_after != '}':
                    body.append(first_after)
                continue
            if started and depth <= 0:
                break
            if started:
                stripped = lines[j].strip()
                if stripped and stripped != '}':
                    body.append(stripped)
        return body


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(SwallowedExceptionsScanner, 'never-swallow-exceptions')
