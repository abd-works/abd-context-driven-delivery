"""Scanner for consistent vocabulary in JavaScript/TypeScript test files.

Detects synonym soup: mixing create/build, get/fetch/retrieve,
delete/remove, update/modify within the same file.
"""

import re
from typing import List, Dict, Any, TYPE_CHECKING
from pathlib import Path
from js_code_scanner import JSCodeScanner
from scanner_bases.violation import Violation

if TYPE_CHECKING:
    from scanner_bases.resources.scan_context import FileScanContext

SYNONYM_GROUPS = [
    ('create', ['build', 'construct', 'make', 'generate', 'produce']),
    ('get', ['fetch', 'retrieve', 'obtain', 'load', 'acquire']),
    ('delete', ['remove', 'destroy', 'erase', 'purge']),
    ('update', ['modify', 'change', 'alter', 'mutate', 'patch']),
    ('send', ['emit', 'dispatch', 'publish', 'broadcast']),
    ('validate', ['verify', 'check', 'assert', 'confirm']),
]

IDENT_RE = re.compile(r'\b([a-zA-Z_]\w*)\b')


class ConsistentVocabularyScanner(JSCodeScanner):

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

        identifiers = {m.group(1).lower() for m in IDENT_RE.finditer(content)}

        for canonical, synonyms in SYNONYM_GROUPS:
            canon_present = any(canonical in ident for ident in identifiers)
            found_synonyms = [
                s for s in synonyms
                if any(s in ident for ident in identifiers)
            ]
            if canon_present and found_synonyms:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'File mixes "{canonical}" with synonym(s) '
                        f'{", ".join(repr(s) for s in found_synonyms)} — '
                        f'pick one term and use it consistently'
                    ),
                    location=str(file_path),
                    line_number=1,
                    severity='warning'
                ).to_dict())
            elif len(found_synonyms) > 1:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'File uses multiple synonyms for the same concept: '
                        f'{", ".join(repr(s) for s in found_synonyms)} — '
                        f'pick one term and use it consistently'
                    ),
                    location=str(file_path),
                    line_number=1,
                    severity='warning'
                ).to_dict())
        return violations
