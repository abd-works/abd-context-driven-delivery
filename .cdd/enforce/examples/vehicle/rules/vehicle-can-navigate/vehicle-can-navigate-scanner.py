"""vehicle-can-navigate — every vehicle scenario must declare a navigation capability.

Scans *.md files for a Vehicle mention. If a Vehicle is mentioned but no
recognised navigation keyword appears in the same scenario block, a violation
is raised.

Usage:
    python vehicle-can-navigate-scanner.py --workspace <path-to-scenarios>

Exit codes:
    0 = no violations
    1 = violations found
    2 = scanner failed to run
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from enforce.scanners.scanners import ArtifactScanner, FileWorkspace, Violation, run  # noqa: E402

_VEHICLE_RE = re.compile(r"\*\*Vehicle\*\*", re.IGNORECASE)

_NAVIGATION_KEYWORDS = (
    "navigation", "gps", "steer", "steering", "autopilot", "compass",
    "waypoint", "route", "helm", "lane-assist", "lane assist",
    "guidance", "directed", "sonar", "radar",
)


def _scenario_blocks(text: str) -> list[tuple[int, str]]:
    """Return (start_lineno, block_text) for each Scenario block."""
    blocks: list[tuple[int, str]] = []
    current_start = 0
    current_lines: list[str] = []
    in_scenario = False

    for lineno, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^#{1,3}\s+Scenario", line, re.IGNORECASE):
            if in_scenario and current_lines:
                blocks.append((current_start, "\n".join(current_lines)))
            current_start = lineno
            current_lines = [line]
            in_scenario = True
        elif in_scenario:
            if re.match(r"^#{1,3}\s+", line) and not re.match(r"^#{1,3}\s+Scenario", line, re.IGNORECASE):
                blocks.append((current_start, "\n".join(current_lines)))
                in_scenario = False
                current_lines = []
            else:
                current_lines.append(line)

    if in_scenario and current_lines:
        blocks.append((current_start, "\n".join(current_lines)))

    return blocks


class VehicleCanNavigateScanner(ArtifactScanner):
    """Every vehicle scenario must declare a navigation capability."""
    rule = "vehicle-can-navigate"
    kind = "quality"
    reads = ("markdown",)

    def scan(self) -> Iterator[Violation]:
        for path in self.workspace.markdown_files():
            yield from _scan_file(path)


def _scan_file(path: Path) -> Iterator[Violation]:
    text = path.read_text(encoding="utf-8")
    for start_line, block in _scenario_blocks(text):
        if not _VEHICLE_RE.search(block):
            continue
        step_lines = "\n".join(block.splitlines()[1:])
        low = step_lines.lower()
        if not any(kw in low for kw in _NAVIGATION_KEYWORDS):
            yield Violation(
                rule="vehicle-can-navigate",
                message="Scenario mentions Vehicle but states no navigation capability",
                location=f"{path.name}:{start_line}",
            )


if __name__ == "__main__":
    sys.exit(run(VehicleCanNavigateScanner))
