"""Scanner: detect classes with too many methods (>10), violating SRP."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

CLASS_PATTERN = re.compile(r'class\s+(\w+)')
METHOD_PATTERN = re.compile(
    r'^\s+(?:async\s+)?(?:static\s+)?(?:get\s+|set\s+)?(\w+)\s*\('
)


class SingleResponsibilityScanner(JsCodeScanner):

    MAX_METHODS = 10

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            lines = content.split('\n')
            self._check_classes(lines, file_path, violations)
        return violations

    def _check_classes(self, lines, file_path, violations):
        i = 0
        while i < len(lines):
            cls_match = CLASS_PATTERN.search(lines[i])
            if cls_match:
                class_name = cls_match.group(1)
                class_line = i + 1
                method_count = 0
                depth = 0
                started = False
                for j in range(i, len(lines)):
                    depth += lines[j].count('{') - lines[j].count('}')
                    if not started and '{' in lines[j]:
                        started = True
                    if started:
                        m = METHOD_PATTERN.match(lines[j])
                        if m and m.group(1) != 'constructor':
                            method_count += 1
                    if started and depth <= 0:
                        break
                if method_count > self.MAX_METHODS:
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Class '{class_name}' has {method_count} methods "
                            f"(max {self.MAX_METHODS}). Split responsibilities."
                        ),
                        'location': str(file_path),
                        'line': class_line,
                    })
            i += 1


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(SingleResponsibilityScanner, 'keep-classes-single-responsibility')
