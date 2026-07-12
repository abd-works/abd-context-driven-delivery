from __future__ import annotations

import importlib.util
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .scanner import Scanner
from .violation import Violation


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
    def __init__(self, module_dir: Path, root_path: Path) -> None:
        self.module_dir = Path(module_dir)
        self.root_path = Path(root_path)

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
