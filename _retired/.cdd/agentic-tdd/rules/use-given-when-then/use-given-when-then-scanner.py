"""use-given-when-then — verify test files subclass AgentTest and use the three Given/When/Then helpers.

Scans test_*.py files (AST). Reports violations when a test class does not
inherit from AgentTest, or when a test method does not call when_agent_invoked
and at least one of ai_judge / given_guidance.

Exit codes: 0 = no violations  1 = violations found  2 = scanner error
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # repo root

from rules.rules import ArtifactScanner, Violation, run  # noqa: E402


def _names_called(func: ast.FunctionDef) -> set[str]:
    """Return all function/method names called anywhere in func body."""
    return {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(func)
        if isinstance(node, ast.Call)
        and isinstance(node.func, (ast.Attribute, ast.Name))
        and (
            isinstance(node.func, ast.Name)
            or isinstance(node.func.attr, str)
        )
    }


def _base_names(cls: ast.ClassDef) -> set[str]:
    return {
        base.id if isinstance(base, ast.Name) else (
            base.attr if isinstance(base, ast.Attribute) else ""
        )
        for base in cls.bases
    }


def _scan_file(path: Path) -> Iterator[Violation]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return

    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef):
            continue
        test_methods = [
            fn for fn in cls.body
            if isinstance(fn, ast.FunctionDef) and fn.name.startswith("test_")
        ]
        if not test_methods:
            continue  # skip helper/data classes with no test methods

        if "AgentTest" not in _base_names(cls):
            yield Violation(
                rule="use-given-when-then",
                message=f"class {cls.name!r} does not subclass AgentTest",
                location=f"{path.name}:{cls.lineno}",
            )
            continue

        for fn in cls.body:
            if not isinstance(fn, ast.FunctionDef):
                continue
            if not fn.name.startswith("test_"):
                continue
            calls = _names_called(fn)
            if "when_agent_invoked" not in calls:
                yield Violation(
                    rule="use-given-when-then",
                    message=f"{fn.name!r} does not call when_agent_invoked",
                    location=f"{path.name}:{fn.lineno}",
                )
            if not (calls & {"ai_judge", "given_guidance"}):
                yield Violation(
                    rule="use-given-when-then",
                    message=f"{fn.name!r} has no Given step (given_guidance / given_context)",
                    location=f"{path.name}:{fn.lineno}",
                )


class UseGivenWhenThenScanner(ArtifactScanner):
    rule = "use-given-when-then"
    kind = "shape"
    reads = ("python",)

    def scan(self) -> Iterator[Violation]:
        for path in self.workspace.root.rglob("test_*.py"):
            if "{" in path.name or "examples" in path.parts:
                continue
            yield from _scan_file(path)


if __name__ == "__main__":
    sys.exit(run(UseGivenWhenThenScanner))
