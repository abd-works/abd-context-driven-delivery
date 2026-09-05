"""Scanner: detect hidden dependency construction inside constructors."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

CONSTRUCTOR_PATTERN = re.compile(r'\bconstructor\s*\(')
NEW_INSTANCE_PATTERN = re.compile(r'new\s+([A-Z]\w+)\s*\(')
CLASS_PATTERN = re.compile(r'class\s+(\w+)')

ALLOWED_TYPES = {
    'Map', 'Set', 'Array', 'Date', 'Error', 'RegExp',
    'Promise', 'WeakMap', 'WeakSet', 'URL', 'URLSearchParams',
    'AbortController', 'FormData', 'Headers', 'Request', 'Response',
    'Event', 'CustomEvent', 'Uint8Array', 'Int32Array',
}


class ExplicitDependenciesScanner(JsCodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            lines = content.split('\n')
            class_name = ''
            in_constructor = False
            ctor_depth = 0

            for i, line in enumerate(lines):
                cls = CLASS_PATTERN.search(line)
                if cls:
                    class_name = cls.group(1)

                if CONSTRUCTOR_PATTERN.search(line):
                    in_constructor = True
                    ctor_depth = 0

                if in_constructor:
                    ctor_depth += line.count('{') - line.count('}')
                    match = NEW_INSTANCE_PATTERN.search(line)
                    if match:
                        dep_name = match.group(1)
                        if dep_name not in ALLOWED_TYPES:
                            violations.append({
                                'rule': self.rule,
                                'message': (
                                    f"Hidden dependency 'new {dep_name}()' constructed "
                                    f"inside constructor of '{class_name}'. "
                                    "Inject via constructor parameter instead."
                                ),
                                'location': str(file_path),
                                'line': i + 1,
                            })
                    if ctor_depth <= 0 and '{' in line:
                        in_constructor = False
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(ExplicitDependenciesScanner, 'use-explicit-dependencies')
