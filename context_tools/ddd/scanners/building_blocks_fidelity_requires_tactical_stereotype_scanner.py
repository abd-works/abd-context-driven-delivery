"""Scanner: building-blocks sketches must tag every class with a DDD stereotype."""
from __future__ import annotations

import re
from pathlib import Path

from scanners import Scanner, ScannerRunner

RULE = "building-blocks-fidelity-requires-tactical-stereotype"
_PASCAL = re.compile(r"\b([A-Z][A-Za-z0-9]+)\b")
_STEREOTYPE = re.compile(r"<<[^>]+>>")
_SKIP_PREFIXES = (
    "fidelity:",
    "direction:",
    "crosses:",
    "integrate:",
    "pattern:",
    "invariants:",
    "cross-agg",
    "cross-bc",
    "sync objects",
    "architecture",
)
_FIELD_PREFIXES = ("members:", "repo:", "events:")
_SUFFIXES = frozenset({".md", ".txt"})


class BuildingBlocksFidelityRequiresTacticalStereotypeScanner(Scanner):
    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if file_path.suffix.lower() not in _SUFFIXES:
            return []
        content = file_path.read_text(encoding="utf-8", errors="replace")
        if "fidelity: building_blocks" not in content:
            return []
        violations = []
        for index, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            lower = stripped.lower()
            if any(lower.startswith(prefix) for prefix in _SKIP_PREFIXES):
                continue
            indent = len(line) - len(line.lstrip(" "))
            if any(lower.startswith(prefix) for prefix in _FIELD_PREFIXES):
                rest = stripped.split(":", 1)[1]
                for part in rest.split(";"):
                    if _PASCAL.search(part) and not _STEREOTYPE.search(part):
                        token = _PASCAL.search(part).group(1)
                        violations.append(
                            self.violation(
                                f"Class '{token}' is missing a tactical stereotype "
                                "(<<Entity>>, <<Value Object>>, <<Repository>>, …).",
                                location=str(file_path),
                                line=index,
                            )
                        )
                continue
            if indent == 0:
                continue
            if _PASCAL.match(stripped) and not _STEREOTYPE.search(stripped):
                token = _PASCAL.match(stripped).group(1)
                violations.append(
                    self.violation(
                        f"Class '{token}' is missing a tactical stereotype "
                        "(<<Aggregate Root>>, <<Entity>>, <<Value Object>>, …).",
                        location=str(file_path),
                        line=index,
                    )
                )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            BuildingBlocksFidelityRequiresTacticalStereotypeScanner,
            RULE,
            lambda root: sorted(root.rglob("*.md")),
        )
    )
