"""Draw.io scanners and the inlined scan engine (no ``actions/scan``)."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import inspect
import re
import sys
from abc import ABC
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Type

from practices.clean_engineering.model.drawio import drawio_tools

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
DRAWIO_EXTENSIONS = frozenset({".drawio", ".xml"})


class Violation:
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


class Scanner(ABC):
    """Scan a named rule over files under *root*."""

    _explicit_paths: frozenset[Path] = frozenset()

    def __init__(self, rule: str) -> None:
        self.rule = rule

    @staticmethod
    @contextmanager
    def explicitly_requested(paths: Iterable[Path]) -> Iterator[None]:
        previous = Scanner._explicit_paths
        Scanner._explicit_paths = frozenset(Path(path).resolve() for path in paths)
        try:
            yield
        finally:
            Scanner._explicit_paths = previous

    @staticmethod
    def is_skipped_path(path: Path) -> bool:
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


@dataclass
class ScannerReport:
    violations: list[Violation] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": len(self.violations) == 0,
            "rules": self.rules,
            "violations": [item.to_dict() for item in self.violations],
        }


class ScannerCollection:
    def __init__(
        self,
        module_dir: Path | None = None,
        root_path: Path | None = None,
    ) -> None:
        if module_dir is None:
            module_dir = self._default_module_dir()
        self.module_dir = Path(module_dir)
        self.root_path = (
            Path(root_path) if root_path is not None else self.module_dir / "scanners"
        )

    @staticmethod
    def _default_module_dir() -> Path:
        frame = inspect.currentframe()
        try:
            caller = frame.f_back.f_back if frame and frame.f_back else None
            while caller is not None:
                owner = caller.f_locals.get("self")
                if owner is not None:
                    directory = getattr(owner, "module_dir", None)
                    if directory is not None:
                        return Path(directory)
                caller = caller.f_back
        finally:
            del frame
        return Path.cwd()

    def discover(self) -> dict[str, type[Scanner]]:
        discovered: dict[str, type[Scanner]] = {}
        if not self.root_path.is_dir():
            return discovered
        for script in sorted(self.root_path.glob("*_scanner.py")):
            if script.name in {"code_scanner.py", "js_code_scanner.py"}:
                continue
            scanner_class = self._load_scanner_class(script)
            if scanner_class is None:
                continue
            slug = self._rule_slug_from_script(script, scanner_class)
            discovered[slug] = scanner_class
        return discovered

    def catalog(self) -> str:
        slugs = sorted(self.discover())
        return "\n".join(f"- `{slug}`" for slug in slugs)

    def get(self, slug: str) -> type[Scanner] | None:
        return self.discover().get(slug)

    def run(self, root: Path, files: list[Path]) -> ScannerReport:
        discovered = self.discover()
        files = Scanner.filter_scan_files(files)
        violations: list[Violation] = []
        for slug, scanner_class in discovered.items():
            scanner = scanner_class(slug)
            violations.extend(scanner.scan(root, files))
        return ScannerReport(violations=violations, rules=sorted(discovered))

    def _load_scanner_class(self, script: Path) -> type[Scanner] | None:
        sys.path.insert(0, str(script.parent))
        try:
            spec = importlib.util.spec_from_file_location(script.stem, script)
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for value in vars(module).values():
                if isinstance(value, type) and issubclass(value, Scanner) and value is not Scanner:
                    if value.__module__ == module.__name__:
                        return value
            return None
        finally:
            if str(script.parent) in sys.path:
                sys.path.remove(str(script.parent))

    @staticmethod
    def _rule_slug_from_script(script: Path, scanner_class: type[Scanner]) -> str:
        rule = getattr(scanner_class, "RULE", None)
        if isinstance(rule, str) and rule.strip():
            return rule.strip()
        text = script.read_text(encoding="utf-8")
        match = re.search(r"run_scanner_main\([^,]+,\s*['\"]([^'\"]+)['\"]", text)
        if match:
            return match.group(1)
        return ScannerCollection._slug_from_filename(script.stem)

    @staticmethod
    def _slug_from_filename(stem: str) -> str:
        cleaned = stem
        if cleaned.endswith("_scanner"):
            cleaned = cleaned[: -len("_scanner")]
        return cleaned.replace("_", "-")


class ScanReport:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.ok = bool(payload.get("ok", True))
        self.violations = list(payload.get("violations") or [])
        self.payload = payload

    @classmethod
    def from_scan(cls, raw: str | dict[str, Any] | ScanReport) -> ScanReport:
        if isinstance(raw, ScanReport):
            return raw
        payload = ast.literal_eval(raw) if isinstance(raw, str) else raw
        return cls(payload)

    def matches(self, mistake: Any) -> bool:
        rule = str(getattr(mistake, "rule", "") or "")
        artifact = str(getattr(mistake, "artifact", "") or "")
        artifact_name = Path(artifact).name if artifact else ""
        for violation in self.violations:
            if rule and str(violation.get("rule") or "") != rule:
                continue
            location = str(violation.get("location") or "")
            if artifact and artifact not in location and artifact_name not in location:
                if location:
                    continue
            return True
        return False


class Scan:
    def __init__(self, collection: ScannerCollection | None = None, guidance: Any = None) -> None:
        self._bound_collection = collection
        self._guidance = guidance

    @classmethod
    def bound_to(cls, guidance: Any, collection: ScannerCollection | None = None) -> Scan:
        return cls(collection=collection, guidance=guidance)

    def _scanner_collection(self) -> ScannerCollection:
        if self._bound_collection is not None:
            return self._bound_collection
        guidance = self._guidance
        if guidance is not None:
            return guidance._scanner_collection()
        raise ValueError("Scan needs a scanner collection")

    def _run(
        self,
        collection: ScannerCollection,
        paths: list[str],
        root: str | None,
        rule: str | None,
    ) -> str:
        files = [Path(path) for path in paths]
        scan_root = Path(root) if root is not None else Path.cwd()
        with Scanner.explicitly_requested(files):
            report = collection.run(scan_root, files)
        result = report.to_dict()
        if rule is not None:
            result["violations"] = [v for v in result["violations"] if v["rule"] == rule]
            result["ok"] = len(result["violations"]) == 0
        return str(result)

    def scan(
        self,
        paths: list[str],
        root: str | None = None,
        rule: str | None = None,
        guidance: Any = None,
    ) -> str:
        if guidance is None or isinstance(guidance, str):
            return self._run(self._scanner_collection(), paths, root, rule)
        return self._run(guidance._scanner_collection(), paths, root, rule)


class ScannerRunner:
    @staticmethod
    def execute_scan(
        scanner_class: Type[Any],
        rule: str,
        root: Path,
        files: list[Path],
    ) -> list[Violation]:
        scanner = scanner_class(rule)
        return scanner.scan(root, Scanner.filter_scan_files(files))

    @staticmethod
    def print_violations(violations: list[Violation]) -> None:
        for violation in violations:
            print(violation.to_dict(), file=sys.stderr)

    @staticmethod
    def violations_exit_code(violations: list[Violation]) -> int:
        if not violations:
            return 0
        ScannerRunner.print_violations(violations)
        return 1

    @staticmethod
    def run_scanner_main(
        scanner_class: Type[Any],
        rule: str,
        collect_files: Callable[[Path], list[Path]],
        argv: list[str] | None = None,
    ) -> int:
        parser = argparse.ArgumentParser(description="Run one scanner")
        parser.add_argument(
            "--workspace",
            type=Path,
            default=Path.cwd(),
            help="Project root (default: cwd).",
        )
        args = parser.parse_args(argv)
        root = args.workspace.resolve()
        files = collect_files(root)
        violations = ScannerRunner.execute_scan(scanner_class, rule, root, files)
        return ScannerRunner.violations_exit_code(violations)


run_scanner_main = ScannerRunner.run_scanner_main


class DrawioScanner(Scanner):
    """Scanners that read `.drawio` mxfile pages via ``drawio_tools``."""

    def scan_file(self, root: Path, file_path: Path) -> list:
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


def collect_drawio_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in DRAWIO_EXTENSIONS:
            continue
        if Scanner.is_skipped_path(path):
            continue
        files.append(path)
    return files
