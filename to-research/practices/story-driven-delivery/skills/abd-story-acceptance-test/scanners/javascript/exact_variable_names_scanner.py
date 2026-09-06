"""Scanner for exact variable names in JavaScript/TypeScript test files.

Detects vague variable names: generic names like result, output, data,
value, response, expected without domain qualifiers. Flags overly short
names (1-2 chars except i, j, k).
"""

import re
from typing import List, Dict, Any, Set, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

GENERIC_NAMES: Set[str] = {
    'result', 'output', 'data', 'value', 'response', 'expected',
    'item', 'obj', 'thing', 'tmp', 'temp', 'val', 'res', 'ret',
    'info', 'payload',
}
ALLOWED_SHORT = {'i', 'j', 'k', 'x', 'y', '_'}

VAR_DECL_RE = re.compile(
    r'(?:const|let|var)\s+(?:\{[^}]*\}|(\w+))\s*=', re.MULTILINE
)
DESTRUCTURE_RE = re.compile(
    r'(?:const|let|var)\s+\{([^}]+)\}\s*=', re.MULTILINE
)


class ExactVariableNamesScanner(JSCodeScanner):

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

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue

            for m in VAR_DECL_RE.finditer(line):
                name = m.group(1)
                if not name:
                    continue
                self._check_name(name, i + 1, file_path, violations)

            for m in DESTRUCTURE_RE.finditer(line):
                names = [n.strip().split(':')[0].strip() for n in m.group(1).split(',')]
                for name in names:
                    if name:
                        self._check_name(name, i + 1, file_path, violations)

        return violations

    def _check_name(self, name: str, line_no: int, file_path: Path,
                    violations: list) -> None:
        if name.lower() in GENERIC_NAMES:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    f'Variable "{name}" uses a generic name — use an exact '
                    f'domain-specific name from the scenario or acceptance criteria'
                ),
                location=str(file_path),
                line_number=line_no,
                severity='warning'
            ).to_dict())
        elif len(name) <= 2 and name not in ALLOWED_SHORT:
            violations.append(Violation(
                rule=self.rule,
                violation_message=(
                    f'Variable "{name}" is too short — use a descriptive '
                    f'domain name instead of single-letter abbreviation'
                ),
                location=str(file_path),
                line_number=line_no,
                severity='warning'
            ).to_dict())
