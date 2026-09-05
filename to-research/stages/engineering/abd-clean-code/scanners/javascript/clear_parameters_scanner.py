"""Scanner: detect functions with too many parameters (>5)."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

FUNC_WITH_PARAMS = re.compile(
    r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?)'
    r'\(([^)]*)\)'
)
METHOD_WITH_PARAMS = re.compile(
    r'^\s+(?:async\s+)?(?:static\s+)?(\w+)\s*\(([^)]*)\)'
)


class ClearParametersScanner(JsCodeScanner):

    MAX_PARAMS = 5

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            for i, line in enumerate(content.split('\n')):
                fn = FUNC_WITH_PARAMS.search(line)
                if fn:
                    name = fn.group(1) or fn.group(2) or '<anonymous>'
                    params = fn.group(3)
                    count = self._count_params(params)
                    if count > self.MAX_PARAMS:
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Function '{name}' has {count} parameters "
                                f"(max {self.MAX_PARAMS}). "
                                "Group into an options object."
                            ),
                            'location': str(file_path),
                            'line': i + 1,
                        })
                    continue
                mt = METHOD_WITH_PARAMS.search(line)
                if mt:
                    name = mt.group(1)
                    params = mt.group(2)
                    count = self._count_params(params)
                    if count > self.MAX_PARAMS:
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Method '{name}' has {count} parameters "
                                f"(max {self.MAX_PARAMS}). "
                                "Group into an options object."
                            ),
                            'location': str(file_path),
                            'line': i + 1,
                        })
        return violations

    @staticmethod
    def _count_params(param_str):
        stripped = param_str.strip()
        if not stripped:
            return 0
        return len([p for p in stripped.split(',') if p.strip()])


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(ClearParametersScanner, 'use-clear-function-parameters')
