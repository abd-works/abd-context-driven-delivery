"""Scanner for detecting test helpers with too many primitive parameters."""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')

_HELPER_PATTERNS = [
    re.compile(r'function\s+(create|build|make|setup|prepare|generate)\w*\s*\(([^)]*)\)'),
    re.compile(r'(?:const|let|var)\s+(create|build|make|setup|prepare|generate)\w*\s*=\s*(?:async\s*)?\(([^)]*)\)'),
    re.compile(r'(?:const|let|var)\s+(create|build|make|setup|prepare|generate)\w*\s*=\s*function\s*\(([^)]*)\)'),
]

_TS_PRIMITIVE = re.compile(
    r':\s*(?:string|number|boolean|null|undefined)\b'
)

MAX_PRIMITIVE_PARAMS = 4


class ObjectOrientedHelpersScanner(JSCodeScanner):
    """Checks that test helpers use objects/classes for context rather than many primitives."""

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in _JS_EXTS):
            return violations
        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in _HELPER_PATTERNS:
                m = pattern.search(line)
                if not m:
                    continue
                func_name_prefix = m.group(1)
                params_str = m.group(2).strip()
                if not params_str:
                    continue

                full_params = params_str
                if params_str.count('(') > params_str.count(')'):
                    for extra in lines[line_num:min(line_num + 3, len(lines))]:
                        full_params += extra
                        if ')' in extra:
                            break

                params = [p.strip() for p in full_params.split(',') if p.strip()]
                if len(params) <= MAX_PRIMITIVE_PARAMS:
                    continue

                destructured = any('{' in p for p in params)
                if destructured:
                    continue

                primitive_count = self._count_primitives(params, path_str.endswith('.ts') or path_str.endswith('.tsx'))
                if primitive_count > MAX_PRIMITIVE_PARAMS:
                    full_name = re.search(r'((?:create|build|make|setup|prepare|generate)\w*)', line)
                    name = full_name.group(1) if full_name else func_name_prefix
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Helper "{name}" takes {primitive_count} primitive parameters. '
                            f'Use an options object or builder pattern instead (max {MAX_PRIMITIVE_PARAMS}).'
                        ),
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict())
                break

        return violations

    def _count_primitives(self, params: list, is_typescript: bool) -> int:
        if is_typescript:
            return sum(1 for p in params if _TS_PRIMITIVE.search(p) or ':' not in p)
        return len(params)
