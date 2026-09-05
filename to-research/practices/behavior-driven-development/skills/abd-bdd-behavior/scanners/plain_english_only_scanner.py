#!/usr/bin/env python3
"""Scanner for plain-english-only rule.

Checks that *-hierarchy.txt scaffold files contain no code syntax.
Code characters like (), =>, {}, [], ; signal premature implementation
leaking into the behavior scaffold.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Path setup for standalone execution; run_scanners.py sets PYTHONPATH automatically.
_SKILL_ROOT = Path(__file__).resolve().parent.parent
_ABD_SKILLS = _SKILL_ROOT.parent.parent.parent.parent
for _p in (_ABD_SKILLS / 'common' / 'scripts',):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from scanner_runner import execute_scan_with_workspace  # noqa: E402
from scanner_bases import Scanner, Violation, FileCollection, ScanFilesContext  # noqa: E402

if False:  # TYPE_CHECKING
    from scanner_bases.resources.scan_context import FileScanContext

_CODE_SYNTAX = re.compile(r'[()=>{}\[\];]|=>|\.\.\.')

_ALLOWED_EXCEPTIONS = re.compile(
    r'^\s*#|^\s*//|HIERARCHY|^\s*$',
    re.IGNORECASE,
)


class PlainEnglishOnlyScanner(Scanner):
    """Flags code syntax characters in BDD scaffold hierarchy files."""

    def scan_file_with_context(self, context: 'FileScanContext') -> list:
        if not context.exists or not context.file_path:
            return []
        name = context.file_path.name.lower()
        if not (name.endswith('-hierarchy.txt') or name.endswith('_hierarchy.txt') or name == 'hierarchy.txt'):
            return []
        try:
            content = context.file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return []

        violations = []
        for i, line in enumerate(content.splitlines(), 1):
            if _ALLOWED_EXCEPTIONS.search(line):
                continue
            m = _CODE_SYNTAX.search(line)
            if m:
                char = m.group(0)
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Code syntax "{char}" found in scaffold — '
                        f'hierarchy must be plain English only. '
                        f'Remove implementation detail from behavior description.'
                    ),
                    location=str(context.file_path),
                    line_number=i,
                    severity='error',
                ).to_dict())
        return violations


def _build_context(workspace: Path, story_graph_path: Path | None) -> ScanFilesContext:
    from scanner_runner import load_workspace_graph_json
    hierarchy_files = list(workspace.rglob('*hierarchy*.txt'))
    files = FileCollection(test_files=hierarchy_files)
    return ScanFilesContext(
        story_graph=load_workspace_graph_json(workspace, story_graph_path),
        files=files,
    )


if __name__ == '__main__':
    sys.exit(execute_scan_with_workspace(
        PlainEnglishOnlyScanner,
        'plain-english-only',
        _build_context,
    ))
