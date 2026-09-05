"""Scanner for business-readable test names in JavaScript/TypeScript.

Ensures test names use domain language. Flags generic names like
"test1", "should work", "handles correctly", and abbreviations.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

TEST_NAME_RE = re.compile(
    r'''(?:it|test)\s*\(\s*['"`](.+?)['"`]''', re.IGNORECASE
)
GENERIC_PATTERNS = [
    re.compile(r'^test\s*\d+$', re.IGNORECASE),
    re.compile(r'^should\s+work$', re.IGNORECASE),
    re.compile(r'^handles?\s+correctly$', re.IGNORECASE),
    re.compile(r'^works?\s*$', re.IGNORECASE),
    re.compile(r'^it\s+does\s+something$', re.IGNORECASE),
    re.compile(r'^basic\s+test$', re.IGNORECASE),
    re.compile(r'^default\s+case$', re.IGNORECASE),
    re.compile(r'^happy\s+path$', re.IGNORECASE),
]
ABBREVIATION_RE = re.compile(r'\b(cfg|mgr|svc|obj|req|resp|impl|util|init)\b', re.IGNORECASE)


class BusinessReadableTestNamesScanner(JSCodeScanner):

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
            m = TEST_NAME_RE.search(line)
            if not m:
                continue
            test_name = m.group(1)
            line_no = i + 1

            for pat in GENERIC_PATTERNS:
                if pat.search(test_name):
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Test name "{test_name}" is too generic — use domain '
                            f'language that describes observable behavior'
                        ),
                        location=str(file_path),
                        line_number=line_no,
                        severity='warning'
                    ).to_dict())
                    break
            else:
                abbr = ABBREVIATION_RE.search(test_name)
                if abbr:
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Test name "{test_name}" contains abbreviation '
                            f'"{abbr.group(1)}" — use full business-readable words'
                        ),
                        location=str(file_path),
                        line_number=line_no,
                        severity='warning'
                    ).to_dict())
                elif len(test_name.split()) < 3 and len(test_name) < 15:
                    violations.append(Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Test name "{test_name}" is too short — add context '
                            f'about the behavior being verified'
                        ),
                        location=str(file_path),
                        line_number=line_no,
                        severity='warning'
                    ).to_dict())
        return violations
