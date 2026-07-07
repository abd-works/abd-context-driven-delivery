"""Scanner framework for enforce rules.

Every scanner is a subclass of :class:`ArtifactScanner` that implements
``scan()`` and yields :class:`Violation` records.

The module-level ``run(scanner_cls)`` helper wires argparse and stdout
emission so every scanner has the same CLI:

    python <rule>-scanner.py --workspace <path>

Contract:
- Scanner receives a :class:`FileWorkspace` and reads files from it.
- ``scan()`` yields :class:`Violation` records.
- rule id is declared as a class attribute.

Output:
- Human-readable violation lines on **stdout**
- Summary line on **stdout**
- Exit 0 = no violations, 1 = violations found, 2 = scanner failed to run
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterator, Literal, Optional, Sequence


# ---------------------------------------------------------------------------
# Violation
# ---------------------------------------------------------------------------

@dataclass
class Violation:
    rule: str
    message: str
    location: str
    severity: str = "warning"
    hint: Optional[str] = None

    def __str__(self) -> str:
        hint_part = f"  hint: {self.hint}" if self.hint else ""
        return f"FAIL  {self.location}: {self.message}{hint_part}"


# ---------------------------------------------------------------------------
# FileWorkspace
# ---------------------------------------------------------------------------

@dataclass
class FileWorkspace:
    """Minimal workspace: a directory of files for scanners to read."""
    root: Path

    @classmethod
    def load(cls, root: Path) -> "FileWorkspace":
        return cls(root=root.resolve())

    def markdown_files(self) -> list[Path]:
        return sorted(self.root.rglob("*.md"))

    def files(self, pattern: str = "**/*") -> list[Path]:
        return sorted(self.root.glob(pattern))


# ---------------------------------------------------------------------------
# ArtifactScanner
# ---------------------------------------------------------------------------

ArtifactKind = Literal["markdown", "story_map", "thin_slice", "scenarios", "tests"]


class ArtifactScanner:
    """Base class for every enforce scanner.

    Subclasses declare:
      - ``rule``  — kebab-case rule id
      - ``kind``  — "shape" or "quality"
      - ``reads`` — tuple of artifact kinds the scanner needs (informational)

    And implement:
      - ``scan() -> Iterator[Violation]``
    """
    rule: str = ""
    kind: Literal["shape", "quality"] = "quality"
    reads: Sequence[ArtifactKind] = ("markdown",)

    def __init__(self, workspace: FileWorkspace) -> None:
        self.workspace = workspace

    def scan(self) -> Iterator[Violation]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Scanner discovery and loading
# ---------------------------------------------------------------------------

def load_scanner(scanner_path: Path) -> ModuleType:
    """Dynamically load a scanner module from a file path."""
    spec = importlib.util.spec_from_file_location(scanner_path.stem, scanner_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {scanner_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[scanner_path.stem] = mod  # required for modules with hyphens in name
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def find_scanner_class(mod: ModuleType) -> type | None:
    """Return the first ArtifactScanner subclass defined in the module."""
    for _, obj in inspect.getmembers(mod, inspect.isclass):
        if issubclass(obj, ArtifactScanner) and obj is not ArtifactScanner and obj.__module__ == mod.__name__:
            return obj
    return None


def rule_name_from_scanner(scanner_path: Path) -> str:
    """vehicle-can-navigate-scanner.py → vehicle-can-navigate"""
    return scanner_path.stem.removesuffix("-scanner")


def discover_scanners(rules_dir: Path, rule: str | None) -> list[tuple[str, Path]]:
    """Return [(rule_name, scanner_path)] for all scanners matching the optional filter."""
    results: list[tuple[str, Path]] = []
    for scanner_path in sorted(rules_dir.rglob("*-scanner.py")):
        name = rule_name_from_scanner(scanner_path)
        if rule is None or name == rule:
            results.append((name, scanner_path))
    return results


def run_on_file(scanner_cls: type, target: Path) -> list[Violation]:
    """Run a scanner against a single file; filter violations to that file only."""
    workspace = FileWorkspace.load(target.parent)
    scanner = scanner_cls(workspace=workspace)
    return [
        v for v in scanner.scan()
        if Path(v.location.split(":")[0]) == target or v.location.startswith(target.name)
    ]


# ---------------------------------------------------------------------------
# Module-level CLI  (python -m enforce.scanners validate <file> ...)
# ---------------------------------------------------------------------------

def validate(target: Path, rules_dir: Path, rule: str | None = None) -> int:
    """Validate a single file against one or all scanners. Returns exit code."""
    from enforce.rules.rules import infer_rule  # noqa: PLC0415

    if not target.is_file():
        print(f"enforce: file not found: {target}", file=sys.stderr)
        return 2

    rule_filter = rule or infer_rule(target, rules_dir)
    found = discover_scanners(rules_dir, rule_filter)
    if not found:
        label = f"rule '{rule_filter}'" if rule_filter else "any rule"
        print(f"enforce: no scanner found for {label} in {rules_dir}", file=sys.stderr)
        return 2

    overall = 0
    for rule_name, scanner_path in found:
        try:
            mod = load_scanner(scanner_path)
            scanner_cls = find_scanner_class(mod)
            if scanner_cls is None:
                raise RuntimeError(f"no ArtifactScanner subclass in {scanner_path.name}")
            violations = run_on_file(scanner_cls, target)
        except Exception as exc:
            print(f"Rule: {rule_name} -> ERROR  ({exc})", file=sys.stderr)
            overall = max(overall, 2)
            continue

        if violations:
            for v in violations:
                print(f"  {v}", file=sys.stderr)
            print(f"Rule: {rule_name} -> FAIL")
            overall = max(overall, 1)
        else:
            print(f"Rule: {rule_name} -> PASS")

    return overall


def main() -> int:
    """CLI entry point: python -m enforce.scanners validate <file> [--rule <name>] [--rules-dir <path>]"""
    _default_rules_dir = Path(__file__).parents[1] / "examples"

    parser = argparse.ArgumentParser(prog="enforce.scanners", description="Run enforce scanners against an artifact.")
    sub = parser.add_subparsers(dest="command", required=True)
    val = sub.add_parser("validate", help="Validate a file against one or all scanners.")
    val.add_argument("file")
    val.add_argument("--rule", default=None)
    val.add_argument("--rules-dir", default=str(_default_rules_dir))

    args = parser.parse_args()
    return validate(
        target=Path(args.file).resolve(),
        rules_dir=Path(args.rules_dir).resolve(),
        rule=args.rule,
    )


# ---------------------------------------------------------------------------
# CLI runner (for individual scanner scripts)
# ---------------------------------------------------------------------------

def run(scanner_cls: type) -> int:
    """Wire argparse + stdout for a scanner; return exit code."""
    parser = argparse.ArgumentParser(description=scanner_cls.__doc__ or "enforce scanner")
    parser.add_argument("--workspace", required=True, help="Root folder to scan")
    args = parser.parse_args()

    root = Path(args.workspace).resolve()

    try:
        workspace = FileWorkspace.load(root)
        scanner = scanner_cls(workspace=workspace)
        violations = list(scanner.scan())
    except Exception as exc:
        import traceback
        print(f"# {scanner_cls.__name__} failed: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 2

    for v in violations:
        print(v)

    count = len(violations)
    if count:
        print(f"\n# {scanner_cls.__name__}: {count} violation(s) for rule {scanner_cls.rule!r}")
        return 1
    print(f"# {scanner_cls.__name__}: OK — 0 violations for rule {scanner_cls.rule!r}")
    return 0
