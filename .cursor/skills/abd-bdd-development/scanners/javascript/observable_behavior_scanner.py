#!/usr/bin/env python3
"""Scanner for observable-behavior rule (abd-bdd-development).

Checks that BDD test files do not assert on private/internal state.
Tests must assert observable outcomes through the public API only.
Flags: expect(x._field), direct _property access, private method calls.
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

_EXPECT_PRIVATE = re.compile(r'expect\s*\([^)]*\._\w+')
_DIRECT_PRIVATE = re.compile(
    r'(?:result|output|instance|obj|subject|sut|actual)\s*\.\s*_\w+'
)
_PRIVATE_METHOD_CALL = re.compile(
    r'(?:result|output|instance|obj|subject|sut)\s*\.\s*_\w+\s*\('
)


class ObservableBehaviorScanner(Scanner):
    """Detects assertions on private state — tests must use public API."""

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

        violations = []
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('//'):
                continue

            if _EXPECT_PRIVATE.search(stripped):
                field = re.search(r'\._(\w+)', stripped)
                name = field.group(1) if field else 'private field'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Assertion accesses private field "_{name}". '
                        f'Assert observable behavior through the public API.'
                    ),
                    location=str(context.file_path),
                    line_number=i,
                    severity='warning',
                ).to_dict())
                continue

            if _PRIVATE_METHOD_CALL.search(stripped):
                method = re.search(r'\.(_\w+)\s*\(', stripped)
                name = method.group(1) if method else '_method'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test calls private method "{name}". '
                        f'Test through the public interface to verify observable behavior.'
                    ),
                    location=str(context.file_path),
                    line_number=i,
                    severity='warning',
                ).to_dict())
                continue

            if _DIRECT_PRIVATE.search(stripped) and 'expect' not in stripped:
                field = re.search(r'\.(_\w+)', stripped)
                name = field.group(1) if field else '_field'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Test accesses private member "{name}". '
                        f'Verify behavior through the public API.'
                    ),
                    location=str(context.file_path),
                    line_number=i,
                    severity='info',
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
        ObservableBehaviorScanner,
        'observable-behavior',
        _build_context,
    ))
