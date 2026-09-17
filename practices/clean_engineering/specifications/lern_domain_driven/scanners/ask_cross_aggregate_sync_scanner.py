"""Scanner: cross-aggregate slices record the sync choice from AskQuestion."""
from __future__ import annotations

from pathlib import Path
from typing import List

from lern_scanner_base import LERNScanner
from scan.violation import Violation

_HEADING = "cross-aggregate sync"
_CHOICE_MARKERS = (
    "event-based",
    "event based",
    "direct repository",
    "direct calls",
    "single-aggregate",
    "single aggregate",
)


class AskCrossAggregateSyncScanner(LERNScanner):
    """When two or more aggregates exist, grill-answers must record the sync choice."""

    RULE = "ask-cross-aggregate-sync"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        domains = self._find_domain_packages(root)
        if len(domains) < 2:
            return []

        answers = self._read_grill_answers(root)
        if answers is None:
            return [
                self.v(
                    "This slice has more than one aggregate and no "
                    ".context/grill-answers.md. AskQuestion for cross-aggregate "
                    "sync (event-based orchestration vs direct repository calls "
                    "by the client) before generating stories.",
                    str(root),
                )
            ]

        lower = answers.lower()
        if _HEADING not in lower:
            return [
                self.v(
                    ".context/grill-answers.md is missing heading 'Cross-aggregate sync'. "
                    "AskQuestion and record event-based orchestration, direct "
                    "repository calls by the client, or single-aggregate.",
                    str(self._grill_answers_path(root)),
                )
            ]
        if not any(marker in lower for marker in _CHOICE_MARKERS):
            return [
                self.v(
                    "Cross-aggregate sync heading is present but no choice is recorded. "
                    "Name event-based orchestration or direct repository calls by the client.",
                    str(self._grill_answers_path(root)),
                )
            ]
        return []

    def _grill_answers_path(self, root: Path) -> Path:
        return root / ".context" / "grill-answers.md"

    def _read_grill_answers(self, root: Path) -> str | None:
        direct = self._grill_answers_path(root)
        if direct.is_file():
            return direct.read_text(encoding="utf-8", errors="replace")
        sessions = root / ".context" / "sessions"
        if sessions.is_dir():
            matches = sorted(sessions.rglob("grill-answers.md"))
            if matches:
                return matches[0].read_text(encoding="utf-8", errors="replace")
        return None
