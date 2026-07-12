"""Scanner: detect JavaScript/TypeScript functions exceeding 20 lines."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner


class FunctionSizeScanner(JsCodeScanner):

    MAX_LINES = 20
    FUNC_PATTERN = re.compile(
        r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
    )

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            content = self._read_file(file_path)
            if content is None:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines):
                match = self.FUNC_PATTERN.search(line)
                if match:
                    func_name = match.group(1) or match.group(2) or '<anonymous>'
                    size = self._count_function_lines(content, i)
                    if size > self.MAX_LINES:
                        violations.append(self.violation(
                            f"Function '{func_name}' is ~{size} lines "
                            f"(max {self.MAX_LINES}). Extract helpers.",
                            location=str(file_path),
                            line=i + 1,
                        ))
        return violations


if __name__ == '__main__':
    from scanners import run_scanner_main
    from js_code_scanner import collect_javascript_files
    raise SystemExit(run_scanner_main(FunctionSizeScanner, 'keep-functions-small-focused', collect_javascript_files))
