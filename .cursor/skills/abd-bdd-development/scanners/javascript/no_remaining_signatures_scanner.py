#!/usr/bin/env python3
"""Scanner for no-remaining-signatures rule (abd-bdd-development).

Checks that completed BDD test files contain no '// BDD: SIGNATURE'
markers. A marker left in means the RED phase is incomplete — the test
body was never implemented.

Only scans files that look like test files (.test.ts, .spec.ts, etc.)
and skips files that appear to be pure signature skeletons (where every
it() body contains only the marker with no other meaningful content).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
_ABD_SKILLS = _SKILL_ROOT.parent.parent.parent.parent
for _p in (_ABD_SKILLS / 'common' / 'scripts',):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from scanner_runner import execute_scan_with_workspace  # noqa: E402
from scanner_bases import Scanner, Violation, FileCollection, ScanFilesContext  # noqa: E402

if False:
    from scanner_bases.resources.scan_context import FileScanContext

_JS_EXTS = ('.ts', '.js', '.tsx', '.jsx', '.mjs')
_BDD_SIGNATURE = '// BDD: SIGNATURE'
# If ALL it() bodies are pure signature, this is still a signature file — skip
_IT_BODY_RE = re.compile(r'it\s*\(', re.IGNORECASE)
_IMPL_INDICATOR = re.compile(
    r'expect\s*\(|\.toBe\(|\.toEqual\(|await\s+|const\s+\w+\s*=',
    re.IGNORECASE,
)


def _is_pure_signature_file(content: str) -> bool:
    """True when the file has no implementation beyond BDD markers."""
    if _BDD_SIGNATURE not in content:
        return False
    return not bool(_IMPL_INDICATOR.search(content))


class NoRemainingSignaturesScanner(Scanner):
    """Flags any '// BDD: SIGNATURE' found in what appears to be a complete test file."""

    def scan_file_with_context(self, context: 'FileScanContext') -> list:
        if not context.exists or not context.file_path:
            return []
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in _JS_EXTS):
            return []
        if '.test.' not in path_str and '.spec.' not in path_str:
            return []

        try:
            content = context.file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return []

        if _BDD_SIGNATURE not in content:
            return []

        # Pure signature files are valid inputs to bdd-development — don't flag them
        if _is_pure_signature_file(content):
            return []

        violations = []
        for i, line in enumerate(content.splitlines(), 1):
            if _BDD_SIGNATURE in line:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'"// BDD: SIGNATURE" marker found in what appears to be a '
                        f'completed test file. Implement the test body and remove the marker.'
                    ),
                    location=str(context.file_path),
                    line_number=i,
                    severity='error',
                ).to_dict())
        return violations


def _build_context(workspace: Path, story_graph_path: Path | None) -> ScanFilesContext:
    from scanner_runner import load_workspace_graph_json
    test_files = [
        f for f in workspace.rglob('*')
        if f.is_file()
        and any(f.name.lower().endswith(ext) for ext in _JS_EXTS)
        and ('.test.' in f.name.lower() or '.spec.' in f.name.lower())
    ]
    files = FileCollection(test_files=test_files)
    return ScanFilesContext(
        story_graph=load_workspace_graph_json(workspace, story_graph_path),
        files=files,
    )


if __name__ == '__main__':
    sys.exit(execute_scan_with_workspace(
        NoRemainingSignaturesScanner,
        'no-remaining-signatures',
        _build_context,
    ))
