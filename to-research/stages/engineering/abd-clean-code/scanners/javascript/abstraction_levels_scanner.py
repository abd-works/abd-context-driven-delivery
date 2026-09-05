"""Scanner: detect functions mixing high-level orchestration with low-level I/O."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

FUNC_PATTERN = re.compile(
    r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
)
LOW_LEVEL_IO = re.compile(
    r'\b(?:fs\.\w+|readFile|writeFile|readdir|fetch\s*\(|'
    r'document\.querySelector|document\.getElementById|'
    r'innerHTML|appendChild|\.query\s*\(|\.execute\s*\(|'
    r'SELECT\s+|INSERT\s+|UPDATE\s+|DELETE\s+)',
    re.IGNORECASE,
)
HIGH_LEVEL_CALL = re.compile(
    r'\b(?:await\s+(?:this\.)?[a-z]\w+\.\w+\(|'
    r'(?:this\.)?[a-z]\w+Service\.|(?:this\.)?[a-z]\w+Repository\.)',
)


class AbstractionLevelsScanner(JsCodeScanner):

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
                has_low = bool(LOW_LEVEL_IO.search(body))
                has_high = bool(HIGH_LEVEL_CALL.search(body))
                if has_low and has_high:
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Function '{func_name}' mixes abstraction levels: "
                            "high-level orchestration with low-level I/O. "
                            "Extract I/O into a separate helper."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(AbstractionLevelsScanner, 'maintain-abstraction-levels')
