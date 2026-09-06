#!/usr/bin/env python3
"""Scanner for business-readable-language rule.

Checks that behavior lines (leaf items in hierarchy scaffold) start with
"should" — the canonical signal that a line describes observable behavior
rather than a category or grouping.

Only leaf lines are checked: lines whose following non-empty sibling or
child has deeper indentation than it (i.e., describe-level lines) are
skipped. A line is a leaf when no subsequent line has greater indentation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parent.parent
_ABD_SKILLS = _SKILL_ROOT.parent.parent.parent.parent
for _p in (_ABD_SKILLS / 'common' / 'scripts',):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from scanner_runner import execute_scan_with_workspace  # noqa: E402
from scanner_bases import Scanner, Violation, FileCollection, ScanFilesContext  # noqa: E402

if False:
    from scanner_bases.resources.scan_context import FileScanContext

_COMMENT = re.compile(r'^\s*(#|//|HIERARCHY)', re.IGNORECASE)
_SHOULD = re.compile(r'^\s*should\b', re.IGNORECASE)
_EMPTY = re.compile(r'^\s*$')


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _leaf_behavior_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Return (lineno, line) pairs for lines that are leaf nodes."""
    result = []
    n = len(lines)
    for i, line in enumerate(lines):
        if _EMPTY.match(line) or _COMMENT.match(line):
            continue
        my_indent = _indent(line)
        # Look ahead: if any following non-empty line has greater indent, this is a describe node.
        is_describe = False
        for j in range(i + 1, n):
            if _EMPTY.match(lines[j]) or _COMMENT.match(lines[j]):
                continue
            if _indent(lines[j]) > my_indent:
                is_describe = True
            break
        if not is_describe:
            result.append((i + 1, line))
    return result


class BusinessReadableLanguageScanner(Scanner):
    """Flags behavior leaf lines that do not start with 'should'."""

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

        lines = content.splitlines()
        violations = []
        for lineno, line in _leaf_behavior_lines(lines):
            stripped = line.strip()
            if not stripped:
                continue
            if not _SHOULD.match(line):
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Behavior line "{stripped}" does not start with "should". '
                        f'Leaf items must describe observable behavior: '
                        f'"should {stripped}" or reword in should-form.'
                    ),
                    location=str(context.file_path),
                    line_number=lineno,
                    severity='warning',
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
        BusinessReadableLanguageScanner,
        'business-readable-language',
        _build_context,
    ))
