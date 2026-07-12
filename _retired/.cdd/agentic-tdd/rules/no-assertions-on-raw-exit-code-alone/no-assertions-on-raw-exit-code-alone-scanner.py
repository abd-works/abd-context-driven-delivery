"""no-assertions-on-raw-exit-code-alone — detect bare assert result.exit_code == 0 with no content check.

Scans test_*.py files (AST). For each test method, reports a violation when
the method contains an `assert ... exit_code ...` expression that compares
exit_code against an integer (0 or 1) and the method contains no call to
ai_judge and no string-content check (e.g. `in result.stdout`).

Exit codes: 0 = no violations  1 = violations found  2 = scanner error
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # repo root

from rules.rules import ArtifactScanner, Violation, run  # noqa: E402


def _has_exit_code_assert(fn: ast.FunctionDef) -> int | None:
    """Return the line number of a bare exit_code comparison assertion, or None."""
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assert):
            continue
        test = node.test
        # assert result.exit_code == 0  or  assert result.exit_code != 1  etc.
        if isinstance(test, ast.Compare):
            left = test.left
            if (
                isinstance(left, ast.Attribute)
                and left.attr == "exit_code"
                and all(isinstance(c, ast.Constant) and isinstance(c.value, int) for c in test.comparators)
            ):
                return node.lineno
    return None


def _has_content_check(fn: ast.FunctionDef) -> bool:
    """Return True if the method calls ai_judge or inspects stdout as a string."""
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else (
                func.id if isinstance(func, ast.Name) else None
            )
            if name == "ai_judge":
                return True
        # `"PASS" in result.stdout`
        if isinstance(node, ast.Compare) and any(isinstance(op, ast.In) for op in node.ops):
            for comp in node.comparators:
                if isinstance(comp, ast.Attribute) and comp.attr in ("stdout", "stderr"):
                    return True
    return False


def _scan_file(path: Path) -> Iterator[Violation]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return

    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef):
            continue
        for fn in cls.body:
            if not isinstance(fn, ast.FunctionDef) or not fn.name.startswith("test_"):
                continue
            lineno = _has_exit_code_assert(fn)
            if lineno and not _has_content_check(fn):
                yield Violation(
                    rule="no-assertions-on-raw-exit-code-alone",
                    message=(
                        f"{fn.name!r} asserts exit_code without checking content "
                        "(add ai_judge or inspect result.stdout)"
                    ),
                    location=f"{path.name}:{lineno}",
                )


class NoExitCodeAloneScanner(ArtifactScanner):
    rule = "no-assertions-on-raw-exit-code-alone"
    kind = "shape"
    reads = ("python",)

    def scan(self) -> Iterator[Violation]:
        for path in self.workspace.root.rglob("test_*.py"):
            if "{" in path.name or "examples" in path.parts:
                continue
            yield from _scan_file(path)


if __name__ == "__main__":
    sys.exit(run(NoExitCodeAloneScanner))
