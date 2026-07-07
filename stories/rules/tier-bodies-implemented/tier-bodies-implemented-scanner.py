"""tier-bodies-implemented — every tier step body has real code.

Textual scan of tier files (`<slug>-<tier>.test.<ext>`, `test_<slug>_<tier>.py`,
`<Slug><Tier>Test.java`). Flags:

- TODO / FIXME / XXX / HACK comments inside a step body.
- Placeholder throws (`raise NotImplementedError`, `throw new Error('not implemented')`).
- Empty step bodies (`() => {}`, `def _step(...): pass`, `void step() {}`).

This runs at engineering fidelity to guard against AI runs that re-emit the
scaffolder's TODO shape instead of actually implementing the tier.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator, List

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402

_TIER_FILE_NAME = re.compile(
    r"(?:^|/)(?P<slug>[a-z0-9][a-z0-9-]+)-(?P<tier>[a-z][a-z0-9]{0,20})\.test\.(?P<ext>ts|tsx|js|jsx)$"
    r"|(?:^|/)test_(?P<py_slug>[a-z0-9_]+)_(?P<py_tier>[a-z][a-z0-9_]{0,20})\.py$"
    r"|(?:^|/)(?P<java_class>[A-Z][A-Za-z0-9]*)(?P<java_tier>[A-Z][A-Za-z0-9]*)Test\.java$"
)

_TODO_MARKERS = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")

# TS/JS/TSX empty arrow body: `(...) => {\n<only whitespace or comments>\n}`
_TS_STEP = re.compile(
    r"['\"`](?P<key>[^'\"`\n]+)['\"`]\s*:\s*(?:async\s*)?\(\s*\)\s*=>\s*\{"
    r"(?P<body>[^{}]*?)\}",
    re.DOTALL,
)

_PY_STEP_DEF = re.compile(
    r"^\s*def\s+_(?:given|when|then)_[a-z0-9_]+\s*\(self[^)]*\)\s*->\s*None\s*:\s*"
    r"(?P<body>(?:\n\s+.+)+?)(?=\n\s*def\s|\Z)",
    re.MULTILINE,
)

_JAVA_STEP_LAMBDA = re.compile(
    r"put\s*\(\s*\"(?P<key>[^\"]+)\"\s*,\s*\(\)\s*->\s*\{(?P<body>[^{}]*?)\}\s*\)",
    re.DOTALL,
)


def _body_is_stub(body: str) -> bool:
    """Return True when the body has no real code (empty, comments-only, or
    a placeholder throw / marker)."""
    stripped_lines: List[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("//") or line.startswith("#"):
            continue
        if line.startswith("/*") or line.startswith("*") or line.startswith("*/"):
            continue
        stripped_lines.append(line)

    if not stripped_lines:
        return True

    joined = "\n".join(stripped_lines)
    if _TODO_MARKERS.search(joined):
        return True
    if re.search(r"raise\s+NotImplementedError\b", joined):
        return True
    if re.search(r"throw\s+new\s+Error\s*\(\s*['\"`]not implemented", joined, re.IGNORECASE):
        return True
    if joined == "pass":
        return True
    if joined in ("{}", "return;", "return null;"):
        return True

    return False


class TierBodiesImplementedScanner(ArtifactScanner):
    """Every step body inside a tier file must contain real code."""
    rule = "tier-bodies-implemented"
    kind = "quality"
    reads = ("test_suites",)

    def scan(self) -> Iterator[Violation]:
        root = self.workspace.root
        for suite in self.workspace.test_suites:
            if suite.source is None:
                continue
            rel_path = suite.source.file
            path = Path(rel_path)
            if not _TIER_FILE_NAME.search(str(rel_path).replace("\\", "/")):
                continue

            full_path = (root / rel_path) if not path.is_absolute() else path
            if not full_path.exists():
                continue
            text = full_path.read_text(encoding="utf-8", errors="replace")

            suffix = path.suffix
            if suffix in {".ts", ".tsx", ".js", ".jsx"}:
                yield from self._scan_ts(rel_path, text)
            elif suffix == ".py":
                yield from self._scan_py(rel_path, text)
            elif suffix == ".java":
                yield from self._scan_java(rel_path, text)

    def _scan_ts(self, rel_path: str, text: str) -> Iterator[Violation]:
        for match in _TS_STEP.finditer(text):
            key = match.group("key")
            body = match.group("body") or ""
            if _body_is_stub(body):
                line_no = text[: match.start()].count("\n") + 1
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Tier step {key!r} in {rel_path} has an unimplemented body — "
                        f"engineering fidelity must produce real code, not scaffolder TODOs"
                    ),
                    location=f"{rel_path}:{line_no}",
                    severity="warning",
                    hint=(
                        "Replace the TODO stub with a real call, await, or assertion. "
                        "The scaffolder emits TODOs only on first bootstrap; from then on "
                        "the human/AI owns the body."
                    ),
                )

    def _scan_py(self, rel_path: str, text: str) -> Iterator[Violation]:
        for match in _PY_STEP_DEF.finditer(text):
            body = match.group("body") or ""
            # Strip the docstring on the first line if present.
            body_lines = body.splitlines()
            body_no_doc = "\n".join(
                line for line in body_lines
                if not re.match(r'^\s*(?:"""|\'\'\')', line)
            )
            if _body_is_stub(body_no_doc):
                line_no = text[: match.start()].count("\n") + 1
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Tier step method in {rel_path} has an unimplemented body — "
                        f"engineering fidelity must produce real code, not scaffolder TODOs"
                    ),
                    location=f"{rel_path}:{line_no}",
                    severity="warning",
                    hint=(
                        "Replace `raise NotImplementedError` with real setup / call / "
                        "assertion. The scaffolder emits stubs only on first bootstrap."
                    ),
                )

    def _scan_java(self, rel_path: str, text: str) -> Iterator[Violation]:
        for match in _JAVA_STEP_LAMBDA.finditer(text):
            key = match.group("key")
            body = match.group("body") or ""
            if _body_is_stub(body):
                line_no = text[: match.start()].count("\n") + 1
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Tier step {key!r} in {rel_path} has an unimplemented body — "
                        f"engineering fidelity must produce real code, not scaffolder TODOs"
                    ),
                    location=f"{rel_path}:{line_no}",
                    severity="warning",
                    hint=(
                        "Replace the TODO stub with a real call or assertion. The "
                        "scaffolder emits TODOs only on first bootstrap."
                    ),
                )


if __name__ == "__main__":
    sys.exit(run(TierBodiesImplementedScanner))
