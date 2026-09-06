"""Scanner: detect JavaScript/TypeScript functions exceeding 20 lines."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner


class FunctionSizeScanner(JsCodeScanner):

    MAX_LINES = 20
    FUNC_PATTERN = re.compile(
        r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
    )

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines):
                match = self.FUNC_PATTERN.search(line)
                if match:
                    func_name = match.group(1) or match.group(2) or '<anonymous>'
                    size = self._count_function_lines(content, i)
                    if size > self.MAX_LINES:
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Function '{func_name}' is ~{size} lines "
                                f"(max {self.MAX_LINES}). Extract helpers."
                            ),
                            'location': str(file_path),
                            'line': i + 1,
                        })
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(FunctionSizeScanner, 'keep-functions-small-focused')
