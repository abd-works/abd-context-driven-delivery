"""Scanner for ASCII-only in JavaScript/TypeScript code (client and server)."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext


class AsciiOnlyScanner(JSCodeScanner):
    """Detects non-ASCII characters in JavaScript/TypeScript code.
    Equivalent to Python AsciiOnlyScanner: use ASCII-only in source (e.g. [PASS], [ERROR], [FAIL]).
    Works for both client-side and server-side .js/.ts files.
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
        for line_num, line in enumerate(lines, 1):
            v = self._check_unicode_characters(line, file_path, line_num, content)
            if v:
                violations.append(v)
        return violations

    def _check_unicode_characters(
        self, line: str, file_path: Path, line_num: int, content: str
    ) -> Optional[Dict[str, Any]]:
        try:
            line.encode('ascii')
        except UnicodeEncodeError:
            unicode_chars = []
            for char in line:
                try:
                    char.encode('ascii')
                except UnicodeEncodeError:
                    unicode_chars.append(char)
            if unicode_chars:
                problematic = [c for c in unicode_chars if ord(c) > 127]
                if problematic:
                    sample = ', '.join(set(problematic[:3]))
                    msg = (
                        f'Line contains Unicode characters: {sample} - '
                        'use ASCII alternatives like [PASS], [ERROR], [FAIL]'
                    )
                    return Violation(
                        rule=self.rule,
                        violation_message=msg,
                        line_number=line_num,
                        location=str(file_path),
                        severity='error'
                    ).to_dict()
        return None
