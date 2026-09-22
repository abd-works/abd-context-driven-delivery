"""Draw.io layout scanners — self-contained; no Scan kit."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from practices.clean_engineering.model.drawio import drawio_tools

DRAWIO_EXTENSIONS = frozenset({".drawio", ".xml"})

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
_REPAIR_FIXTURE_NAMES = frozenset({"faultyasset", "repairedasset"})
_REPAIR_FIXTURE_DIRS = frozenset({"faultyassets", "repairedassets"})


class DrawioViolation:
    def __init__(
        self,
        rule: str,
        message: str,
        *,
        location: str = "",
        line: int | None = None,
        severity: str = "error",
    ) -> None:
        self.rule = rule
        self.message = message
        self.location = location
        self.line = line
        self.severity = severity

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "violation_message": self.message,
            "severity": self.severity,
            "line_number": self.line,
            "location": self.location,
        }


class DrawioScanner:
    """Scanners that read `.drawio` mxfile pages via ``drawio_tools``."""

    _explicit_paths: frozenset[Path] = frozenset()

    def __init__(self, rule: str | None = None) -> None:
        self.rule = rule or getattr(type(self), "RULE", type(self).__name__)

    @staticmethod
    @contextmanager
    def explicitly_requested(paths: Iterable[Path]) -> Iterator[None]:
        previous = DrawioScanner._explicit_paths
        DrawioScanner._explicit_paths = frozenset(
            Path(path).resolve() for path in paths
        )
        try:
            yield
        finally:
            DrawioScanner._explicit_paths = previous

    @staticmethod
    def is_skipped_path(path: Path) -> bool:
        p = Path(path)
        if DrawioScanner._explicit_paths and p.resolve() in DrawioScanner._explicit_paths:
            return False
        if p.stem.lower() in _REPAIR_FIXTURE_NAMES:
            return False
        if any(part.lower() in _REPAIR_FIXTURE_DIRS for part in p.parts):
            return False
        return any(part in SKIP_DIR_NAMES for part in p.parts)

    @staticmethod
    def filter_scan_files(files: list[Path]) -> list[Path]:
        return [path for path in files if not DrawioScanner.is_skipped_path(path)]

    def scan(self, root: Path, files: list[Path]) -> list[DrawioViolation]:
        root = root.resolve()
        violations: list[DrawioViolation] = []
        for file_path in DrawioScanner.filter_scan_files(files):
            path = file_path if file_path.is_absolute() else root / file_path
            if not path.is_file():
                continue
            if DrawioScanner.is_skipped_path(path):
                continue
            violations.extend(self.scan_file(root, path))
        return violations

    def scan_file(self, root: Path, file_path: Path) -> list[DrawioViolation]:
        del root
        if file_path.suffix.lower() not in DRAWIO_EXTENSIONS:
            return []
        try:
            _, mxfile = drawio_tools.load_drawio(str(file_path))
        except Exception as exc:  # noqa: BLE001 - surface as a scan violation
            return [
                self.violation(
                    f"Could not load drawio file: {exc}",
                    location=str(file_path),
                )
            ]
        violations = []
        for diagram in mxfile.findall("diagram"):
            page_name = diagram.get("name") or "(unnamed)"
            _, page_root = drawio_tools.get_page(mxfile, page_name)
            if page_root is None:
                continue
            violations.extend(self.scan_page(file_path, page_name, page_root))
        return violations

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        return []

    def violation(
        self,
        message: str,
        *,
        location: str = "",
        line: int | None = None,
        severity: str = "error",
    ) -> DrawioViolation:
        return DrawioViolation(
            self.rule,
            message,
            location=location,
            line=line,
            severity=severity,
        )

    @classmethod
    def discover(cls) -> dict[str, type[DrawioScanner]]:
        discovered: dict[str, type[DrawioScanner]] = {}
        scanners_dir = Path(__file__).resolve().parent
        for script in sorted(scanners_dir.glob("*_scanner.py")):
            scanner_class = cls._load_scanner_class(script)
            if scanner_class is None:
                continue
            slug = getattr(scanner_class, "RULE", None)
            if not isinstance(slug, str) or not slug.strip():
                stem = script.stem
                if stem.endswith("_scanner"):
                    stem = stem[: -len("_scanner")]
                slug = stem.replace("_", "-")
            discovered[slug.strip()] = scanner_class
        return discovered

    @classmethod
    def _load_scanner_class(cls, script: Path) -> type[DrawioScanner] | None:
        parent = str(script.parent)
        sys.path.insert(0, parent)
        # Scanners import ``_drawio_base`` by filename; alias this module so
        # they subclass the same DrawioScanner this discoverer is checking.
        previous_alias = sys.modules.get("_drawio_base")
        sys.modules["_drawio_base"] = sys.modules[cls.__module__]
        try:
            spec = importlib.util.spec_from_file_location(script.stem, script)
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for value in vars(module).values():
                if (
                    isinstance(value, type)
                    and issubclass(value, DrawioScanner)
                    and value is not DrawioScanner
                    and value.__module__ == module.__name__
                ):
                    return value
            return None
        finally:
            if previous_alias is None:
                sys.modules.pop("_drawio_base", None)
            else:
                sys.modules["_drawio_base"] = previous_alias
            if parent in sys.path:
                sys.path.remove(parent)

    @classmethod
    def run_report(
        cls,
        paths: list[str],
        root: str | Path | None = None,
        rule: str | None = None,
    ) -> dict[str, Any]:
        scan_root = Path(root) if root is not None else Path.cwd()
        files = [Path(path) for path in paths]
        discovered = cls.discover()
        with cls.explicitly_requested(files):
            violations: list[DrawioViolation] = []
            for slug, scanner_class in discovered.items():
                violations.extend(scanner_class(slug).scan(scan_root, files))
        result = {
            "ok": len(violations) == 0,
            "rules": sorted(discovered),
            "violations": [item.to_dict() for item in violations],
        }
        if rule is not None:
            result["violations"] = [
                item for item in result["violations"] if item["rule"] == rule
            ]
            result["ok"] = len(result["violations"]) == 0
        return result

    @classmethod
    def run_main(cls, argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description="Run one Draw.io scanner")
        parser.add_argument(
            "--workspace",
            type=Path,
            default=Path.cwd(),
            help="Project root (default: cwd).",
        )
        args = parser.parse_args(argv)
        workspace = args.workspace.resolve()
        files = collect_drawio_files(workspace)
        scanner = cls(getattr(cls, "RULE", cls.__name__))
        violations = scanner.scan(workspace, files)
        if not violations:
            return 0
        for violation in violations:
            print(violation.to_dict(), file=sys.stderr)
        return 1


def collect_drawio_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in DRAWIO_EXTENSIONS:
            continue
        if DrawioScanner.is_skipped_path(path):
            continue
        files.append(path)
    return files
