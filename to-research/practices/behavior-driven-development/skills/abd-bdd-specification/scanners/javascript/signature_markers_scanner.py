#!/usr/bin/env python3
"""Scanner for signature-markers rule.

Checks that every it() block body in BDD signature files contains exactly
'// BDD: SIGNATURE' and nothing else (no implementation, no assertions).

A signature file is identified by the presence of '// BDD: SIGNATURE'
anywhere in the file — this distinguishes it from completed test files.
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
_TEST_MARKERS = ('.test.', '.spec.')

# Matches: it('...', () => { or it("...", async () => {
_IT_OPEN = re.compile(
    r'''(?:^|\s)it\s*\(\s*['"`](.+?)['"`]\s*,\s*(?:async\s*)?\(?\s*\)?\s*=>\s*\{''',
    re.MULTILINE,
)
_BDD_SIGNATURE = '// BDD: SIGNATURE'

# Lines inside a test body that indicate real implementation
_IMPL_PATTERNS = re.compile(
    r'expect\s*\(|\.toBe\(|\.toEqual\(|\.toHaveBeenCalled|'
    r'\.toBeTruthy|\.toBeFalsy|\.toContain\(|'
    r'await\s+|const\s+\w+\s*=|let\s+\w+\s*=|return\s+\w',
    re.IGNORECASE,
)


def _is_signature_file(content: str) -> bool:
    return _BDD_SIGNATURE in content


def _extract_it_bodies(content: str) -> list[tuple[int, str, str]]:
    """Return list of (line_number, test_name, body_content) for each it() block."""
    results = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        m = _IT_OPEN.search(line)
        if not m:
            continue
        test_name = m.group(1)
        # Find the matching closing brace
        depth = 0
        start_line = i
        body_lines = []
        in_body = False

        for j in range(i, min(i + 30, len(lines))):
            l = lines[j]
            for ch in l:
                if ch == '{':
                    depth += 1
                    if depth == 1:
                        in_body = True
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        break
            if in_body and depth > 0:
                body_lines.append(l)
            if depth == 0 and in_body:
                break

        body = '\n'.join(body_lines)
        results.append((start_line + 1, test_name, body))

    return results


class SignatureMarkersScanner(Scanner):
    """Flags it() bodies in signature files that are missing or have extras beyond the marker."""

    def scan_file_with_context(self, context: 'FileScanContext') -> list:
        if not context.exists or not context.file_path:
            return []
        path_str = str(context.file_path).lower()
        if not any(path_str.endswith(ext) for ext in _JS_EXTS):
            return []
        if not any(m in path_str for m in _TEST_MARKERS):
            return []

        try:
            content = context.file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return []

        if not _is_signature_file(content):
            return []

        violations = []
        for lineno, test_name, body in _extract_it_bodies(content):
            has_marker = _BDD_SIGNATURE in body
            has_impl = bool(_IMPL_PATTERNS.search(body))

            if not has_marker:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'it("{test_name}") body missing "// BDD: SIGNATURE" marker. '
                        f'Signature files must contain only the marker — no implementation.'
                    ),
                    location=str(context.file_path),
                    line_number=lineno,
                    severity='error',
                ).to_dict())
            elif has_impl:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=(
                        f'it("{test_name}") body has implementation beyond the marker. '
                        f'Remove all logic — keep only "// BDD: SIGNATURE".'
                    ),
                    location=str(context.file_path),
                    line_number=lineno,
                    severity='error',
                ).to_dict())

        return violations


def _build_context(workspace: Path, story_graph_path: Path | None) -> ScanFilesContext:
    from scanner_runner import load_workspace_graph_json
    test_files = [
        f for f in workspace.rglob('*')
        if f.is_file()
        and any(f.name.lower().endswith(ext) for ext in _JS_EXTS)
        and any(m in f.name.lower() for m in ('.test.', '.spec.'))
    ]
    files = FileCollection(test_files=test_files)
    return ScanFilesContext(
        story_graph=load_workspace_graph_json(workspace, story_graph_path),
        files=files,
    )


if __name__ == '__main__':
    sys.exit(execute_scan_with_workspace(
        SignatureMarkersScanner,
        'signature-markers',
        _build_context,
    ))
