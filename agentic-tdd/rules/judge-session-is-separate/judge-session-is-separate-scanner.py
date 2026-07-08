"""judge-session-is-separate — detect when ai_judge reuses the same session_file as when_agent_invoked.

Scans test_*.py files (AST). For each test method, collects the string literal
values passed as session_file= to when_agent_invoked and ai_judge. Reports a
violation when the same literal path appears in both calls.

Exit codes: 0 = no violations  1 = violations found  2 = scanner error
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # repo root

from rules.rules import ArtifactScanner, Violation, run  # noqa: E402


def _session_file_value(call: ast.Call) -> str | None:
    """Return the string literal passed as session_file=, or None."""
    for kw in call.keywords:
        if kw.arg == "session_file":
            # match / or string constants inside the expression
            node = kw.value
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            # e.g. SESSION_DIR / "foo.json"  — grab the right-hand string
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                if isinstance(node.right, ast.Constant) and isinstance(node.right.value, str):
                    return node.right.value
    return None


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

            agent_sessions: list[tuple[int, str]] = []
            judge_sessions: list[tuple[int, str]] = []

            for node in ast.walk(fn):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                name = func.attr if isinstance(func, ast.Attribute) else (
                    func.id if isinstance(func, ast.Name) else None
                )
                val = _session_file_value(node)
                if val is None:
                    continue
                if name == "when_agent_invoked":
                    agent_sessions.append((node.lineno, val))
                elif name == "ai_judge":
                    judge_sessions.append((node.lineno, val))

            agent_vals = {v for _, v in agent_sessions}
            for lineno, val in judge_sessions:
                if val in agent_vals:
                    yield Violation(
                        rule="judge-session-is-separate",
                        message=(
                            f"{fn.name!r} passes the same session_file {val!r} "
                            "to both when_agent_invoked and ai_judge"
                        ),
                        location=f"{path.name}:{lineno}",
                    )


class JudgeSessionIsSeparateScanner(ArtifactScanner):
    rule = "judge-session-is-separate"
    kind = "shape"
    reads = ("python",)

    def scan(self) -> Iterator[Violation]:
        for path in self.workspace.root.rglob("test_*.py"):
            if "{" in path.name or "examples" in path.parts:
                continue
            yield from _scan_file(path)


if __name__ == "__main__":
    sys.exit(run(JudgeSessionIsSeparateScanner))
