"""rules — generate compliant artifacts, validate artifacts against rules, build and test rules.

A *Rule* lives in ``{rule-name}/`` and optionally has an associated scanner.
The :class:`Rule` dataclass provides a typed view of that folder.
The scanner framework (:class:`ArtifactScanner`, :class:`Violation`, :class:`FileWorkspace`)
is bundled here so scanners can import from a single, stable location:

    from rules.rules import ArtifactScanner, Violation, run
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterator, Literal, Optional, Sequence

# ---------------------------------------------------------------------------
# Bootstrap CapabilityCli from capability
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[1]
_CDD_CAP = _REPO_ROOT / "capability" / "capability.py"
_spec = importlib.util.spec_from_file_location("capability", _CDD_CAP)
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("capability", _mod)
_spec.loader.exec_module(_mod)

Capability = _mod.Capability
_BaseCli = _mod.CapabilityCli

_CAPABILITY_ROOT = Path(__file__).resolve().parent
_RULES_DIR = _CAPABILITY_ROOT / "rules"


# ===========================================================================
# Rule
# ===========================================================================

@dataclass
class Rule:
    """A single rule folder: definition, optional scanner, and examples.

    Structure::

        rules/{name}/
            {name}-rule.md          ← rule definition (required)
            {name}-scanner.py       ← mechanical checker (optional)
            examples/
                pass/               ← compliant artifacts
                fail/               ← violating artifacts
    """
    path: Path

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def definition(self) -> Path:
        return self.path / f"{self.name}-rule.md"

    @property
    def scanner_path(self) -> Path | None:
        p = self.path / f"{self.name}-scanner.py"
        return p if p.is_file() else None

    @property
    def has_scanner(self) -> bool:
        return self.scanner_path is not None

    @property
    def examples_pass(self) -> list[Path]:
        d = self.path / "examples" / "pass"
        return sorted(d.glob("*")) if d.is_dir() else []

    @property
    def examples_fail(self) -> list[Path]:
        d = self.path / "examples" / "fail"
        return sorted(d.glob("*")) if d.is_dir() else []


def discover_rules(rules_dir: Path, rule: str | None = None) -> list[Rule]:
    """Return Rule objects under rules_dir, optionally filtered by name."""
    if not rules_dir.is_dir():
        return []
    rules = [
        Rule(d) for d in sorted(rules_dir.iterdir())
        if d.is_dir() and not d.name.startswith("{")
    ]
    if rule:
        rules = [r for r in rules if r.name == rule]
    return rules


def infer_rule(file: Path, rules_dir: Path) -> str | None:
    """Infer rule name from a file path inside the rules tree."""
    try:
        rel = file.resolve().relative_to(rules_dir.resolve())
    except ValueError:
        return None
    for i, seg in enumerate(rel.parts[:-1]):
        if seg == "rules":
            return rel.parts[i + 1]
    # If the file is directly inside rules/{name}/examples/…
    if len(rel.parts) >= 2:
        return rel.parts[0]
    return None


# ===========================================================================
# Scanner framework
# ===========================================================================

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


@dataclass
class FileWorkspace:
    """A directory of files for scanners to read."""
    root: Path

    @classmethod
    def load(cls, root: Path) -> "FileWorkspace":
        return cls(root=root.resolve())

    def markdown_files(self) -> list[Path]:
        return sorted(self.root.rglob("*.md"))

    def files(self, pattern: str = "**/*") -> list[Path]:
        return sorted(self.root.glob(pattern))


ArtifactKind = Literal["markdown", "story_map", "thin_slice", "scenarios", "tests", "python"]


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
# Scanner loading and discovery
# ---------------------------------------------------------------------------

def load_scanner(scanner_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(scanner_path.stem, scanner_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {scanner_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[scanner_path.stem] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def find_scanner_class(mod: ModuleType) -> type | None:
    for _, obj in inspect.getmembers(mod, inspect.isclass):
        if issubclass(obj, ArtifactScanner) and obj is not ArtifactScanner and obj.__module__ == mod.__name__:
            return obj
    return None


def run_on_file(scanner_cls: type, target: Path) -> list[Violation]:
    """Run a scanner against a single file; return violations for that file."""
    workspace = FileWorkspace.load(target.parent)
    scanner = scanner_cls(workspace=workspace)
    return [
        v for v in scanner.scan()
        if Path(v.location.split(":")[0]) == target or v.location.startswith(target.name)
    ]


def run(scanner_cls: type) -> int:
    """Wire argparse + stdout for an individual scanner script; return exit code.

    Every scanner script calls this::

        if __name__ == "__main__":
            sys.exit(run(MyScanner))
    """
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


# ===========================================================================
# validate() — run scanners against a file
# ===========================================================================

def validate(target: Path, rules_dir: Path, rule: str | None = None) -> int:
    """Validate a single file against one or all rule scanners. Returns exit code."""
    if not target.is_file():
        print(f"enforce: file not found: {target}", file=sys.stderr)
        return 2

    rule_filter = rule or infer_rule(target, rules_dir)
    rules = discover_rules(rules_dir, rule_filter)
    scannable = [r for r in rules if r.has_scanner]

    if not scannable:
        label = f"rule '{rule_filter}'" if rule_filter else "any rule"
        print(f"enforce: no scanner found for {label} in {rules_dir}", file=sys.stderr)
        return 2

    overall = 0
    for r in scannable:
        try:
            mod = load_scanner(r.scanner_path)
            scanner_cls = find_scanner_class(mod)
            if scanner_cls is None:
                raise RuntimeError(f"no ArtifactScanner subclass in {r.scanner_path.name}")
            violations = run_on_file(scanner_cls, target)
        except Exception as exc:
            print(f"Rule: {r.name} -> ERROR  ({exc})", file=sys.stderr)
            overall = max(overall, 2)
            continue

        if violations:
            for v in violations:
                print(f"  {v}", file=sys.stderr)
            print(f"Rule: {r.name} -> FAIL")
            overall = max(overall, 1)
        else:
            print(f"Rule: {r.name} -> PASS")

    return overall


# ===========================================================================
# CLI
# ===========================================================================

class CapabilityCli(_BaseCli):
    """enforce capability CLI."""

    def _dispatch(self, args, parser):
        if args.command == "validate":
            return self._validate(args)
        if args.command == "fix":
            return self._fix(args)
        if args.command == "test":
            return self._test(args)
        return super()._dispatch(args, parser)

    def _build_parser(self):
        parser = super()._build_parser()
        sub = parser._subparsers._group_actions[0]

        vp = sub.add_parser("validate", help="Validate a file against one or all rule scanners")
        vp.add_argument("file", help="Path to the artifact file")
        vp.add_argument("--rule", default=None, help="Limit to a single rule name")
        vp.add_argument("--rules-dir", default=str(_RULES_DIR), help="Rules directory")

        fp = sub.add_parser("fix", help="Validate, report violations, and fix the artifact")
        fp.add_argument("file", help="Path to the artifact file to fix")
        fp.add_argument("--rule", default=None, help="Limit to a single rule name")
        fp.add_argument("--rules-dir", default=str(_RULES_DIR), help="Rules directory")

        tp = sub.add_parser("test", help="Run rule and scanner tests")
        tp.add_argument("-v", "--verbose", action="store_true")
        tp.add_argument("--scanner", action="store_true", help="Run scanner tests instead of rule tests")
        tp.add_argument("path", nargs="?")
        return parser

    def _validate(self, args) -> int:
        return validate(
            target=Path(args.file).resolve(),
            rules_dir=Path(args.rules_dir).resolve(),
            rule=args.rule,
        )

    def _fix(self, args) -> int:
        """Run scanners, print report, then signal the agent to apply fixes."""
        target = Path(args.file).resolve()
        rules_dir = Path(args.rules_dir).resolve()
        rc = validate(target=target, rules_dir=rules_dir, rule=args.rule)
        if rc == 0:
            print(f"✓ {target.name}: no violations — nothing to fix")
        else:
            print(f"\nFix {target} to resolve the violations above, then re-run validate.")
        return rc

    def _test(self, args) -> int:
        if args.scanner:
            default_path = _CAPABILITY_ROOT / "validate-artifact-scanner-test.py"
        else:
            default_path = _CAPABILITY_ROOT / "validate-artifact-rules-test.py"
        path = args.path or str(default_path)
        cmd = [sys.executable, "-m", "pytest", path]
        if args.verbose:
            cmd += ["-v", "-s"]
        return subprocess.run(cmd).returncode


# ===========================================================================
# Entry point
# ===========================================================================

def main(argv=None) -> int:
    cap = Capability(_CAPABILITY_ROOT)
    return CapabilityCli(cap).execute(argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
