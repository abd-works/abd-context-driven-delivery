"""Scanner: detect excessive nesting depth (>3) in control flow."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

CONTROL_OPEN = re.compile(
    r'\b(?:if|else\s+if|else|for|while|switch|do)\b.*\{'
)
FUNC_PATTERN = re.compile(
    r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
)


class SimplifyControlFlowScanner(JsCodeScanner):

    MAX_DEPTH = 3

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            lines = content.split('\n')
            control_depth = 0
            max_depth = 0
            func_name = None
            func_line = 0
            func_depth = 0
            in_func = False

            for i, line in enumerate(lines):
                fn = FUNC_PATTERN.search(line)
                if fn:
                    if in_func and max_depth > self.MAX_DEPTH:
                        self._add_violation(
                            violations, func_name, max_depth,
                            file_path, func_line,
                        )
                    func_name = fn.group(1) or fn.group(2) or '<anonymous>'
                    func_line = i + 1
                    func_depth = 0
                    control_depth = 0
                    max_depth = 0
                    in_func = True

                if in_func:
                    opens = line.count('{')
                    closes = line.count('}')
                    if CONTROL_OPEN.search(line):
                        control_depth += 1
                        max_depth = max(max_depth, control_depth)
                    control_depth -= closes
                    if control_depth < 0:
                        control_depth = 0
                    func_depth += opens - closes
                    if func_depth <= 0 and in_func and i > func_line:
                        if max_depth > self.MAX_DEPTH:
                            self._add_violation(
                                violations, func_name, max_depth,
                                file_path, func_line,
                            )
                        in_func = False

            if in_func and max_depth > self.MAX_DEPTH:
                self._add_violation(
                    violations, func_name, max_depth, file_path, func_line,
                )
        return violations

    def _add_violation(self, violations, func_name, depth, file_path, line):
        violations.append({
            'rule': self.rule,
            'message': (
                f"Function '{func_name}' nests {depth} levels deep "
                f"(max {self.MAX_DEPTH}). Use early returns or extract helpers."
            ),
            'location': str(file_path),
            'line': line,
        })


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(SimplifyControlFlowScanner, 'simplify-control-flow')
