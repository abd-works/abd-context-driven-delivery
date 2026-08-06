"""Scanner: `business-readable-language` — leaf observations start with should.

Rule: business-readable-language

Every leaf behavior must read as an observable outcome in the domain's language.
In sketches that means leaf lines start with `should` / `it should`. In specs
that means every `it(...)` / `with it(...)` label starts with `should`.

Adapted from abd-skills abd-bdd-behavior for the context-tool sketch + spec model.
"""
from __future__ import annotations

import re
from pathlib import Path

from scanners import Scanner, ScannerRunner

from bdd_scan_helpers import (
    extract_it_blocks,
    is_sketch_file,
    is_spec_file,
    read_text,
)

RULE = "business-readable-language"

_COMMENT = re.compile(r"^\s*(#|//|/\*|Fidelity:|```|HIERARCHY|->)", re.IGNORECASE)
_EMPTY = re.compile(r"^\s*$")
_SHOULD = re.compile(r"^\s*(?:it\s+)?should\b", re.IGNORECASE)
_JAVA_SHOULD = re.compile(r"^should", re.IGNORECASE)


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _leaf_lines(lines: list[str]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    count = len(lines)
    for i, line in enumerate(lines):
        if _EMPTY.match(line) or _COMMENT.match(line):
            continue
        my_indent = _indent(line)
        is_describe = False
        for j in range(i + 1, count):
            if _EMPTY.match(lines[j]) or _COMMENT.match(lines[j]):
                continue
            if _indent(lines[j]) > my_indent:
                is_describe = True
            break
        if not is_describe:
            result.append((i + 1, line))
    return result


class BusinessReadableLanguageScanner(Scanner):
    """Flag leaf behaviors that are not written in should-form."""

    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if is_sketch_file(file_path):
            return self._scan_sketch(file_path)
        if is_spec_file(file_path):
            return self._scan_spec(file_path)
        return []

    def _scan_sketch(self, file_path: Path) -> list:
        content = read_text(file_path)
        if not content:
            return []
        violations = []
        for lineno, line in _leaf_lines(content.splitlines()):
            stripped = line.strip()
            if not stripped or _SHOULD.match(line):
                continue
            violations.append(
                self.violation(
                    f'Behavior line "{stripped}" does not start with "should". '
                    f'Leaf items must describe observable behavior: '
                    f'"should {stripped}" or reword in should-form.',
                    location=str(file_path),
                    line=lineno,
                    severity="warning",
                )
            )
        return violations

    def _scan_spec(self, file_path: Path) -> list:
        content = read_text(file_path)
        if not content:
            return []
        violations = []
        for lineno, label, _body in extract_it_blocks(file_path, content):
            ok = (
                _JAVA_SHOULD.match(label)
                if file_path.suffix.lower() == ".java"
                else _SHOULD.match(label)
            )
            if ok:
                continue
            violations.append(
                self.violation(
                    f'Behavior label "{label}" does not start with "should". '
                    f'Observations must use business-readable should-form.',
                    location=str(file_path),
                    line=lineno,
                    severity="warning",
                )
            )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            BusinessReadableLanguageScanner,
            RULE,
            lambda root: sorted(root.rglob("*")),
        )
    )
