from __future__ import annotations

from abc import ABC
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path

from .violation import Violation

# Directory names excluded from every scan (fixtures, demos, tooling noise).
SKIP_DIR_NAMES = frozenset(
    {
        "node_modules",
        ".git",
        "dist",
        "build",
        "coverage",
        "__pycache__",
        ".venv",
        "venv",
        "examples",
    }
)

# repair.md fixtures live under examples/ by design — keep them scannable.
_REPAIR_FIXTURE_NAMES = frozenset({"faultyasset", "repairedasset"})
_REPAIR_FIXTURE_DIRS = frozenset({"faultyassets", "repairedassets"})


class Scanner(ABC):
    """Scan a named rule over files under *root*."""

    _explicit_paths: frozenset[Path] = frozenset()

    def __init__(self, rule: str) -> None:
        self.rule = rule

    @staticmethod
    @contextmanager
    def explicitly_requested(paths: Iterable[Path]) -> Iterator[None]:
        """Exempt *paths* from directory skipping for the duration of one scan.

        A caller that names a file has already decided it is in scope; the
        skip list exists to keep directory walks from sweeping demos in, not
        to overrule a direct request.
        """
        previous = Scanner._explicit_paths
        Scanner._explicit_paths = frozenset(Path(path).resolve() for path in paths)
        try:
            yield
        finally:
            Scanner._explicit_paths = previous

    @staticmethod
    def is_skipped_path(path: Path) -> bool:
        """True when *path* sits under a skipped directory name (e.g. ``examples/``).

        Repair fixtures (``faultyAsset`` / ``repairedAsset``, any extension -
        ``faultyAsset.py``, ``faultyAsset.md``, ... - or files under
        ``faultyAssets/`` / ``repairedAssets/``) are never skipped — they live
        under ``examples/`` by design and must remain scannable for regression.
        Paths the caller named explicitly are never skipped either.
        """
        p = Path(path)
        if Scanner._explicit_paths and p.resolve() in Scanner._explicit_paths:
            return False
        if p.stem.lower() in _REPAIR_FIXTURE_NAMES:
            return False
        if any(part.lower() in _REPAIR_FIXTURE_DIRS for part in p.parts):
            return False
        return any(part in SKIP_DIR_NAMES for part in p.parts)

    @staticmethod
    def filter_scan_files(files: list[Path]) -> list[Path]:
        """Drop paths under skipped directories so demos do not inflate module metrics."""
        return [path for path in files if not Scanner.is_skipped_path(path)]

    def scan(self, root: Path, files: list[Path]) -> list[Violation]:
        root = root.resolve()
        violations: list[Violation] = []
        for file_path in Scanner.filter_scan_files(files):
            path = file_path if file_path.is_absolute() else root / file_path
            if not path.is_file():
                continue
            if Scanner.is_skipped_path(path):
                continue
            violations.extend(self.scan_file(root, path))
        return violations

    def scan_file(self, root: Path, file_path: Path) -> list[Violation]:
        return []

    def violation(
        self,
        message: str,
        *,
        location: str = "",
        line: int | None = None,
        severity: str = "error",
    ) -> Violation:
        return Violation(
            self.rule,
            message,
            location=location,
            line=line,
            severity=severity,
        )
