"""Scanner: detect catch without parameter, bare re-throw, and overly broad try."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

CATCH_NO_PARAM = re.compile(r'\bcatch\s*\{\s*')
CATCH_WITH_PARAM = re.compile(r'\bcatch\s*\(\s*(\w+)\s*\)')
BARE_THROW = re.compile(r'^\s*throw\s+(\w+)\s*;?\s*$')
TRY_PATTERN = re.compile(r'\btry\s*\{')


class ExceptionHandlingScanner(JsCodeScanner):

    MAX_TRY_LINES = 25

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if CATCH_NO_PARAM.search(line):
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            "Catch block has no error parameter. "
                            "Capture the error to log or wrap it."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
                m = CATCH_WITH_PARAM.search(line)
                if m:
                    param = m.group(1)
                    body = self._catch_body_lines(lines, i)
                    if len(body) == 1 and BARE_THROW.match(body[0]):
                        thrown = BARE_THROW.match(body[0]).group(1)
                        if thrown == param:
                            violations.append({
                                'rule': self.rule,
                                'message': (
                                    f"Catch re-throws '{param}' without adding context. "
                                    "Wrap in a domain error or add a message."
                                ),
                                'location': str(file_path),
                                'line': i + 1,
                            })
                if TRY_PATTERN.search(line):
                    size = self._count_function_lines(content, i)
                    if size > self.MAX_TRY_LINES:
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Try block spans ~{size} lines (max {self.MAX_TRY_LINES}). "
                                "Narrow the try to the risky operation only."
                            ),
                            'location': str(file_path),
                            'line': i + 1,
                        })
        return violations

    @staticmethod
    def _catch_body_lines(lines, catch_line):
        depth = 0
        body = []
        started = False
        for j in range(catch_line, min(catch_line + 30, len(lines))):
            depth += lines[j].count('{') - lines[j].count('}')
            if not started and '{' in lines[j]:
                started = True
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
    run_scanner_main(ExceptionHandlingScanner, 'use-exceptions-properly')
