#!/usr/bin/env python3
"""Scanner for layer-isolation rule (abd-bdd-development).

Checks that mocks in BDD test files target only external boundaries
(APIs, databases, file system, third-party services) — not internal
helper functions or domain logic.

Flags: jest.mock/vi.mock on relative modules, jest.spyOn on internal names.
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

_MOCK_CALL = re.compile(
    r'(?:jest\.mock|jest\.spyOn|vi\.mock|vi\.spyOn|sinon\.stub)\s*\(',
    re.IGNORECASE,
)
_INTERNAL_NAMES = re.compile(
    r'\b(?:validate|calculate|process|format|parse|helper|util|transform|'
    r'convert|normalize|sanitize|build|create|make|compose)\b',
    re.IGNORECASE,
)
_RELATIVE_MODULE = re.compile(
    r'''(?:jest\.mock|vi\.mock)\s*\(\s*['"]\./'''
)


class MockBoundariesScanner(Scanner):
    """Detects mocks of internal code — mocks should target external boundaries only."""

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
            if not _MOCK_CALL.search(line):
                continue

            if _INTERNAL_NAMES.search(line):
                m = _INTERNAL_NAMES.search(line)
                word = m.group(0) if m else 'internal'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Mock targets internal function "{word}". '
                        f'Only mock external boundaries (APIs, databases, third-party services).'
                    ),
                    location=str(context.file_path),
                    line_number=i,
                    severity='warning',
                ).to_dict())
                continue

            if _RELATIVE_MODULE.search(line):
                mod = re.search(r'''['"](\.\/[^'"]+)['"]''', line)
                name = mod.group(1) if mod else 'relative module'
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'jest.mock/vi.mock on relative module "{name}". '
                        f'Prefer mocking external boundaries; call internal code directly.'
                    ),
                    location=str(context.file_path),
                    line_number=i,
                    severity='warning',
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
        MockBoundariesScanner,
        'layer-isolation',
        _build_context,
    ))
