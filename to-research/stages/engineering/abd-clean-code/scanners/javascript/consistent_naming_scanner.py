"""Scanner: detect mixed naming conventions (snake_case vs camelCase) in a file."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

FUNC_PATTERN = re.compile(
    r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
)
SNAKE_CASE = re.compile(r'^[a-z]+(?:_[a-z0-9]+)+$')
CAMEL_CASE = re.compile(r'^[a-z]+(?:[A-Z][a-z0-9]*)+$')
IGNORED_NAMES = {
    'module_exports', 'use_strict', '__dirname', '__filename',
}


class ConsistentNamingScanner(JsCodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            snake_names = []
            camel_names = []
            for i, line in enumerate(content.split('\n')):
                match = FUNC_PATTERN.search(line)
                if not match:
                    continue
                name = match.group(1) or match.group(2) or ''
                if name in IGNORED_NAMES or name.startswith('_'):
                    continue
                if SNAKE_CASE.match(name):
                    snake_names.append((name, i + 1))
                elif CAMEL_CASE.match(name):
                    camel_names.append((name, i + 1))
            if snake_names and camel_names:
                minority = snake_names if len(snake_names) < len(camel_names) else camel_names
                convention = 'camelCase' if len(camel_names) >= len(snake_names) else 'snake_case'
                for name, lineno in minority:
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Function '{name}' breaks the file's dominant "
                            f"{convention} convention. Use consistent naming."
                        ),
                        'location': str(file_path),
                        'line': lineno,
                    })
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(ConsistentNamingScanner, 'use-consistent-naming')
