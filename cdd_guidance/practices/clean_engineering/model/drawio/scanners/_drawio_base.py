"""Draw.io layout scanners: each scanner reads the pages of a `.drawio` file and reports one layout rule."""
from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from harness.graph.violation import Violation
from harness.installation.destination import data_of

from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import DrawioPage

DRAWIO_EXTENSIONS = frozenset({'.drawio', '.xml'})
SKIP_DIR_NAMES = frozenset({'node_modules', '.git', 'dist', 'build', 'coverage', '__pycache__', '.venv', 'venv', 'examples'})
_REPAIR_FIXTURE_NAMES = frozenset({'faultyasset', 'repairedasset'})
_REPAIR_FIXTURE_DIRS = frozenset({'faultyassets', 'repairedassets'})


class DrawioScanner:
    """Scans `.drawio` files page by page. Each subclass names one layout RULE and checks it in `scan_page`."""

    def __init__(self, rule: str | None=None, explicit_paths: Iterable[Path]=(), scan_root: Path | str | None=None) -> None:
        self.rule = rule or getattr(type(self), 'RULE', '')
        # Paths the caller named itself are scanned even inside folders a workspace scan skips.
        self.explicit_paths = frozenset(Path(path).resolve() for path in explicit_paths)
        # The folder a report scans under; without one, the folder the named paths share.
        self.scan_root = Path(scan_root) if scan_root is not None else None

    def is_skipped_path(self, path: Path) -> bool:
        p = Path(path)
        if p.resolve() in self.explicit_paths:
            return False
        if p.stem.lower() in _REPAIR_FIXTURE_NAMES:
            return False
        if any((part.lower() in _REPAIR_FIXTURE_DIRS for part in p.parts)):
            return False
        return any((part in SKIP_DIR_NAMES for part in p.parts))

    def filter_scan_files(self, files: list[Path]) -> list[Path]:
        return [path for path in files if not self.is_skipped_path(path)]

    def scan(self, root: Path, files: list[Path]) -> list[Violation]:
        root = root.resolve()
        violations: list[Violation] = []
        for file_path in self.filter_scan_files(files):
            path = file_path if file_path.is_absolute() else root / file_path
            if not path.is_file():
                continue
            if self.is_skipped_path(path):
                continue
            violations.extend(self.scan_file(root, path))
        return violations

    def scan_file(self, root: Path, file_path: Path) -> list[Violation]:
        del root
        if file_path.suffix.lower() not in DRAWIO_EXTENSIONS:
            return []
        try:
            mxfile = ET.parse(str(file_path)).getroot()
        except (OSError, ET.ParseError) as exc:
            return [Violation(self.rule, f'Could not load drawio file: {exc}', practice='clean_engineering', location=str(file_path))]
        violations = []
        for page in DrawioPage.pages_in(mxfile, file_path):
            violations.extend(self.scan_page(page))
        return violations

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        return []

    def violation(self, page: DrawioPage, message: str) -> Violation:
        """A violation on this page, prefixed with the page name and located at the scanned file."""
        return Violation(self.rule, f'[{page.name or "(unnamed)"}] {message}', practice='clean_engineering', location=str(page.file_path))

    @classmethod
    def discover(cls) -> dict[str, type[DrawioScanner]]:
        discovered: dict[str, type[DrawioScanner]] = {}
        scanners_dir = Path(__file__).resolve().parent
        for script in sorted(scanners_dir.glob('*_scanner.py')):
            scanner_class = cls._scanner_class_in(script)
            if scanner_class is None:
                continue
            slug = getattr(scanner_class, 'RULE', None)
            if not isinstance(slug, str) or not slug.strip():
                slug = script.stem[:-len('_scanner')].replace('_', '-')
            discovered[slug.strip()] = scanner_class
        return discovered

    @staticmethod
    def _scanner_class_in(script: Path) -> type[DrawioScanner] | None:
        module = importlib.import_module(f'{__package__}.{script.stem}')
        for value in vars(module).values():
            if isinstance(value, type) and issubclass(value, DrawioScanner) and value.__module__ == module.__name__:
                return value
        return None

    def run_report(self, paths: list[str]) -> dict[str, Any]:
        files = [Path(path) for path in paths]
        scan_root = self.scan_root or self._shared_folder(files)
        discovered = self.discover()
        violations: list[Violation] = []
        for slug, scanner_class in discovered.items():
            violations.extend(scanner_class(slug, explicit_paths=files).scan(scan_root, files))
        if self.rule:
            violations = [item for item in violations if item.rule == self.rule]
        return {'ok': not violations, 'rules': sorted(discovered), 'violations': data_of(violations)}

    def _shared_folder(self, files: list[Path]) -> Path:
        """The deepest folder that holds every named path, so a report never scans the server's working folder."""
        folders = [path.resolve().parent for path in files]
        shared = folders[0] if folders else Path(__file__).resolve().parent
        while any(shared != folder and shared not in folder.parents for folder in folders):
            shared = shared.parent
        return shared

    def run_main(self, argv: list[str] | None=None) -> int:
        parser = argparse.ArgumentParser(description='Run one Draw.io scanner')
        parser.add_argument('--workspace', type=Path, default=Path.cwd(), help='Project root (default: cwd).')
        args = parser.parse_args(argv)
        workspace = args.workspace.resolve()
        violations = self.scan(workspace, self.collect_drawio_files(workspace))
        for violation in violations:
            print(data_of(violation), file=sys.stderr)
        return 1 if violations else 0

    def collect_drawio_files(self, root: Path) -> list[Path]:
        files: list[Path] = []
        for path in root.rglob('*'):
            if not path.is_file():
                continue
            if path.suffix.lower() not in DRAWIO_EXTENSIONS:
                continue
            if self.is_skipped_path(path):
                continue
            files.append(path)
        return files
