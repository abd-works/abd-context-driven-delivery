"""Scanner for import/require placement in JavaScript/TypeScript (client and server).
Equivalent to Python ImportPlacementScanner: all imports at top of file.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext


class ImportPlacementScanner(JSCodeScanner):
    """Detects import or require statements that appear after non-import code.
    ESM: import x from 'y'; import { a } from 'b'; import 'side-effect';
    CommonJS: require('x'); const x = require('y');
    """

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        violations = []
        if not context.exists or not context.file_path:
            return violations
        path_str = str(context.file_path).lower()
        if not (path_str.endswith('.js') or path_str.endswith('.ts') or path_str.endswith('.mjs') or path_str.endswith('.cjs')):
            return violations
        file_path = context.file_path
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return violations
        lines = content.split('\n')
        import_section_end = self._find_import_section_end(lines)
        violations.extend(self._check_import_placement(lines, import_section_end, file_path))
        return violations

    def _find_import_section_end(self, lines: List[str]) -> int:
        i = 0
        while i < len(lines) and not lines[i].strip():
            i += 1
        in_block_comment = False
        block_comment_start = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if in_block_comment:
                if '*/' in line:
                    in_block_comment = False
                i += 1
                continue
            if '/*' in line and '*/' not in line:
                in_block_comment = True
                i += 1
                continue
            if not stripped or stripped.startswith('//') or (stripped.startswith('/*') and '*/' in line):
                i += 1
                continue
            if self._is_import_or_require(stripped, lines, i):
                i = self._skip_import_or_require(lines, i)
                continue
            break
        return i

    def _is_import_or_require(self, stripped: str, lines: List[str], idx: int) -> bool:
        if stripped.startswith('import '):
            return True
        if re.match(r"^import\s*\(|^import\s*\{|^import\s*\*", stripped):
            return True
        if re.match(r"^const\s+\w+\s*=\s*require\s*\(|^let\s+\w+\s*=\s*require\s*\(", stripped):
            return True
        if re.match(r"^require\s*\(", stripped):
            return True
        if stripped.startswith('import ') or (idx < len(lines) and 'import ' in lines[idx]):
            return True
        return False

    def _skip_import_or_require(self, lines: List[str], start: int) -> int:
        i = start
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue
            if stripped.startswith('//'):
                i += 1
                continue
            if not self._is_import_or_require(stripped, lines, i):
                break
            if ';' in line or (stripped.startswith('import ') and ('from ' in line or "from '" in line or 'from "' in line)):
                i += 1
                continue
            if '(' in line and ')' not in line:
                i += 1
                while i < len(lines) and ')' not in lines[i]:
                    i += 1
                i += 1
                continue
            i += 1
        return i

    def _check_import_placement(
        self, lines: List[str], import_section_end: int, file_path: Path
    ) -> List[Dict[str, Any]]:
        violations = []
        i = import_section_end
        while i < len(lines):
            line = lines[i]
            line_no = i + 1
            stripped = line.strip()
            if not stripped or stripped.startswith('//'):
                i += 1
                continue
            if stripped.startswith('/*'):
                i += 1
                while i < len(lines) and '*/' not in lines[i]:
                    i += 1
                i += 1
                continue
            if self._is_import_or_require(stripped, lines, i):
                violations.append(Violation(
                    rule=self.rule,
                    violation_message='Import statement found after non-import code. Move all imports to the top of the file.',
                    line_number=line_no,
                    location=str(file_path),
                    severity='error'
                ).to_dict())
            i += 1
        return violations
