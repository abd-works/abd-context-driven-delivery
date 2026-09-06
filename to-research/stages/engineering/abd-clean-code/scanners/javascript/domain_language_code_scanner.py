"""Scanner: detect generic class and function names that lack domain language."""
import re
from pathlib import Path
from js_code_scanner import JsCodeScanner

GENERIC_CLASS_NAMES = {
    'Manager', 'Handler', 'Helper', 'Util', 'Utils',
    'Processor', 'Service', 'Controller', 'Base',
}
GENERIC_FUNC_NAMES = {
    'process', 'handle', 'execute', 'run', 'do', 'perform', 'manage',
}

CLASS_PATTERN = re.compile(r'class\s+(\w+)')
FUNC_PATTERN = re.compile(
    r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()'
)


class DomainLanguageCodeScanner(JsCodeScanner):

    def scan(self, context) -> list:
        violations = []
        for file_path in self._get_js_files(context):
            content = self._read_file(Path(file_path))
            if content is None:
                continue
            for i, line in enumerate(content.split('\n')):
                cls = CLASS_PATTERN.search(line)
                if cls:
                    name = cls.group(1)
                    for generic in GENERIC_CLASS_NAMES:
                        if name == generic or name.endswith(generic):
                            violations.append({
                                'rule': self.rule,
                                'message': (
                                    f"Class '{name}' uses generic suffix '{generic}'. "
                                    "Use a domain entity name instead."
                                ),
                                'location': str(file_path),
                                'line': i + 1,
                            })
                            break
                fn = FUNC_PATTERN.search(line)
                if fn:
                    name = fn.group(1) or fn.group(2) or ''
                    if name in GENERIC_FUNC_NAMES:
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Function '{name}' is too generic. "
                                "Use a domain responsibility verb."
                            ),
                            'location': str(file_path),
                            'line': i + 1,
                        })
        return violations


if __name__ == '__main__':
    from js_code_scanner import run_scanner_main
    run_scanner_main(DomainLanguageCodeScanner, 'use-domain-language')
