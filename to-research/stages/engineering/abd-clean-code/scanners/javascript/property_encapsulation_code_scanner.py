"""Scanner: detect public field assignments without encapsulation conventions."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

PUBLIC_FIELD_ASSIGN = re.compile(
    r'this\.([a-zA-Z]\w*)\s*='
)
PRIVATE_PREFIXES = ('#', '_')
CONSTRUCTOR_PATTERN = re.compile(r'\bconstructor\s*\(')
CLASS_PATTERN = re.compile(r'class\s+(\w+)')


class PropertyEncapsulationCodeScanner(JsCodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            lines = content.split('\n')
            in_class = False
            in_constructor = False
            class_name = ''
            depth = 0
            ctor_depth = 0

            for i, line in enumerate(lines):
                cls = CLASS_PATTERN.search(line)
                if cls:
                    in_class = True
                    class_name = cls.group(1)
                    depth = 0

                if in_class:
                    depth += line.count('{') - line.count('}')

                if CONSTRUCTOR_PATTERN.search(line):
                    in_constructor = True
                    ctor_depth = 0

                if in_constructor:
                    ctor_depth += line.count('{') - line.count('}')

                if not in_constructor and in_class:
                    match = PUBLIC_FIELD_ASSIGN.search(line)
                    if match:
                        field = match.group(1)
                        if not field.startswith(PRIVATE_PREFIXES):
                            violations.append({
                                'rule': self.rule,
                                'message': (
                                    f"Public field 'this.{field}' in '{class_name}' "
                                    "assigned outside constructor without # or _ prefix. "
                                    "Encapsulate with getter/setter."
                                ),
                                'location': str(file_path),
                                'line': i + 1,
                            })

                if in_constructor and ctor_depth <= 0 and '{' in line:
                    in_constructor = False
                if in_class and depth <= 0 and i > 0:
                    in_class = False
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(PropertyEncapsulationCodeScanner, 'enforce-encapsulation')
