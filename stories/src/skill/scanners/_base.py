"""Scanner framework — every scanner consumes a Workspace.

A scanner is a subclass of :class:`ArtifactScanner` that implements
``scan(workspace)`` and yields :class:`Violation` records. The module-level
``run(scanner_cls)`` helper wires argparse and stdout emission so every
scanner has the same CLI:

    python <rule>-scanner.py --workspace <path>

Contract:

- Scanner never parses text. Everything goes through the Workspace facade.
- Scanner declares the artifact kinds it reads via `reads` (for the runner).
- Scanner declares its rule id via `rule` and its kind (shape|quality) via `kind`.
- Violations cite `file:line` via the domain node's `source: SourceLocation`.

Output:
- One JSON-per-line violation on **stdout**
- Human summary on **stderr**
- Exit 0 = no violations, 1 = violations found, 2 = scanner failed to run
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, Literal, Optional, Sequence

from stories.src.stories.workspace import Workspace


@dataclass
class Violation:
    rule: str
    message: str
    location: str
    severity: str = "warning"
    hint: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps({k: v for k, v in asdict(self).items() if v is not None})


ArtifactKind = Literal["story_map", "thin_slice", "scenarios", "tests"]


class ArtifactScanner:
    """Base class for every scanner.

    Subclasses set:
      - `rule` — the rule id (kebab-case)
      - `kind` — "shape" or "quality"
      - `reads` — tuple of artifact kinds the scanner needs
    """
    rule: str = ""
    kind: Literal["shape", "quality"] = "quality"
    reads: Sequence[ArtifactKind] = ("story_map",)

    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace

    def scan(self) -> Iterator[Violation]:
        raise NotImplementedError

    def location(self, source, fallback: str = "") -> str:
        """Render a SourceLocation for a Violation."""
        if source is None:
            return fallback
        try:
            return source.render()
        except Exception:
            return fallback


def run(scanner_cls: type) -> int:
    parser = argparse.ArgumentParser(description=scanner_cls.__doc__ or "Stories scanner")
    parser.add_argument("--workspace", default=".", help="Root of the project to scan")
    parser.add_argument("--skill-root", default=None, help="Skill root (accepted for runner compatibility)")
    args = parser.parse_args()

    root = Path(args.workspace).resolve()

    try:
        workspace = Workspace.load(root)
        scanner = scanner_cls(workspace=workspace)
        violations = list(scanner.scan())
    except Exception as exc:
        import traceback
        print(f"# {scanner_cls.__name__} failed: {exc}")
        traceback.print_exc()
        return 2

    for v in violations:
        print(v.to_json())

    count = len(violations)
    if count:
        print(f"# {scanner_cls.__name__}: {count} violation(s) for rule {scanner_cls.rule!r}")
        return 1
    print(f"# {scanner_cls.__name__}: OK for rule {scanner_cls.rule!r}")
    return 0
