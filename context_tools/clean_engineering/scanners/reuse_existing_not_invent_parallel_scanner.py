"""Scanner: reuse-existing-not-invent-parallel

Wrappers/renderers must be named after the wrapped type. Do not invent a
parallel domain noun — especially not a retired synonym (Foundry Practice →
CDD context tool) as a live class, constructor arg, or row/registry/toolset
label.

Exempt: overview lines that *state* the replacement ("context tools replace
practices"); explicit mapping rows ("Practice / plugin → Context tool");
historical recounts of a rejected PracticeEntry parallel schema.
"""
from __future__ import annotations

import re
from pathlib import Path

from scan import Scanner

RULE = "reuse-existing-not-invent-parallel"

_SUFFIXES = frozenset({".md", ".py"})

_CATALOG_PRACTICE = re.compile(r"\bCatalogPractice\b|\bcatalog_practice\b")
_LIVE_PRACTICE = re.compile(
    r"\bpractice[- ]rows?\b|"
    r"\bpractice[- ]registry\b|"
    r"\bpractice[- ]toolsets?\b|"
    r"\bpractice-family\b|"
    r"\bthe practice\s*/\s*context-tool\b",
    re.IGNORECASE,
)
_REPLACE_PRACTICES = re.compile(
    r"\breplace\s+practices?\b",
    re.IGNORECASE,
)
_MAPPING_ROW = re.compile(
    r"Practice\s*/\s*plugin",
    re.IGNORECASE,
)
_REJECTED_PRACTICE_ENTRY = re.compile(
    r"PracticeEntry",
    re.IGNORECASE,
)
_REJECTED_CONTEXT = re.compile(
    r"\breject(?:ed|ion)?\b|\bbefore it was\b|\bwas called\b|\bparallel schema\b",
    re.IGNORECASE,
)


class ReuseExistingNotInventParallelScanner(Scanner):
    """Flag live Practice / CatalogPractice design vocabulary."""

    RULE = RULE

    def scan(self, root: Path, files: list[Path]) -> list:
        # Process/markdown fixtures are often under examples/; do not drop them
        # when the caller passed explicit paths (repair / verify_regression).
        violations = []
        for file_path in files:
            path = file_path if file_path.is_absolute() else Path(root) / file_path
            if not path.is_file() or path.suffix.lower() not in _SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            violations.extend(self._scan_text(path, text))
        return violations

    def _scan_text(self, path: Path, text: str) -> list:
        violations = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            if self._is_exempt(line):
                continue
            if _CATALOG_PRACTICE.search(line):
                violations.append(
                    self.violation(
                        "Live CatalogPractice / catalog_practice invents a parallel "
                        "domain noun. Name the wrapper after the wrapped type "
                        "(CatalogContextTool wraps BaseContextTool).",
                        location=str(path),
                        line=lineno,
                    )
                )
                continue
            if _LIVE_PRACTICE.search(line):
                violations.append(
                    self.violation(
                        "Live 'practice' row/registry/toolset label reuses retired "
                        "Foundry vocabulary. Prefer context-tool rows / registry / "
                        "toolsets (mapping rows that state Practice → Context tool "
                        "are exempt).",
                        location=str(path),
                        line=lineno,
                    )
                )
        return violations

    @staticmethod
    def _is_exempt(line: str) -> bool:
        if _REPLACE_PRACTICES.search(line):
            return True
        if _MAPPING_ROW.search(line):
            return True
        if _REJECTED_PRACTICE_ENTRY.search(line) and _REJECTED_CONTEXT.search(line):
            return True
        return False


def collect_design_files(root: Path) -> list[Path]:
    root = root.resolve()
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in _SUFFIXES
        and not Scanner.is_skipped_path(path)
    )


if __name__ == "__main__":
    from scan import run_scanner_main

    raise SystemExit(
        run_scanner_main(
            ReuseExistingNotInventParallelScanner,
            RULE,
            collect_design_files,
        )
    )
