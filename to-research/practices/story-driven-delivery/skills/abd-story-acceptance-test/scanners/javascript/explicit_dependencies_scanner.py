"""Scanner for explicit dependencies in JavaScript/TypeScript.

Detects `new SomeClass()` inside constructor/function bodies that should
use dependency injection instead of hard-wired construction.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

NEW_INSIDE_BODY_RE = re.compile(
    r'(?:this\.\w+\s*=\s*new\s+(\w+)\s*\(|'
    r'(?:const|let|var)\s+\w+\s*=\s*new\s+(\w+)\s*\()'
)
CLASS_OR_CONSTRUCTOR_RE = re.compile(
    r'(?:constructor\s*\(|class\s+\w+)', re.IGNORECASE
)
ALLOWED_CLASSES = {
    'Date', 'Map', 'Set', 'WeakMap', 'WeakSet', 'Error', 'TypeError',
    'RangeError', 'RegExp', 'URL', 'URLSearchParams', 'Promise',
    'AbortController', 'FormData', 'Headers', 'Request', 'Response',
    'Event', 'CustomEvent', 'Blob', 'File', 'FileReader',
    'Int8Array', 'Uint8Array', 'ArrayBuffer', 'DataView',
}


class ExplicitDependenciesScanner(JSCodeScanner):

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in ('.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx')):
            return violations
        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations
        lines = content.split('\n')

        in_class = False
        brace_depth = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.search(r'\bclass\s+\w+', stripped):
                in_class = True

            if in_class:
                brace_depth += line.count('{') - line.count('}')
                if brace_depth <= 0:
                    in_class = False
                    brace_depth = 0

            if not in_class:
                continue

            m = NEW_INSIDE_BODY_RE.search(line)
            if m:
                class_name = m.group(1) or m.group(2)
                if class_name and class_name not in ALLOWED_CLASSES:
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Dependency "{class_name}" is constructed inline '
                            f'with "new" — inject it via constructor parameter instead'
                        ),
                        location=str(file_path),
                        line_number=i + 1,
                        severity='warning'
                    ).to_dict())
        return violations
