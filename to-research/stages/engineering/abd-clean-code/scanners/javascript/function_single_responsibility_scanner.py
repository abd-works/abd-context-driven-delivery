"""Scanner: detect functions mixing side-effects with pure computation."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

FUNC_PATTERN = re.compile(
    r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
)
SIDE_EFFECTS = re.compile(
    r'\b(?:console\.\w+|fetch\s*\(|axios\.|fs\.\w+|'
    r'writeFile|readFile|localStorage\.|sessionStorage\.|'
    r'document\.\w+|\.innerHTML|process\.exit|'
    r'XMLHttpRequest)',
)
PURE_COMPUTATION = re.compile(
    r'\breturn\s+(?!void\b|undefined\b|null\b|;)'
)


class FunctionSingleResponsibilityScanner(JsCodeScanner):

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
                body = '\n'.join(lines[i + 1:i + size])

                side_effects = SIDE_EFFECTS.findall(body)
                returns = PURE_COMPUTATION.findall(body)
                if side_effects and returns:
                    effects = ', '.join(sorted(set(side_effects)))[:50]
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Function '{func_name}' mixes side-effects "
                            f"({effects}) with return computation. "
                            "Separate into a pure function and a side-effectful caller."
                        ),
                        'location': str(file_path),
                        'line': i + 1,
                    })
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(FunctionSingleResponsibilityScanner, 'keep-functions-single-responsibility')
