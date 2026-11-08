"""The handoff a ticket writes for its session as a person leaves it, closing it or switching to another, so the next
session starts from where this one stopped."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from space.kanban.ticket import FidelityProgress, Ticket

# The latest lines of the session's log the handoff quotes: enough to show the last loop of work, short enough to read.
LOG_LINES_QUOTED = 12


class LeavingHandoff:
    """A handoff in the shape HANDOFF-FORMAT.md gives, written from what the ticket records rather than from a
    conversation: the stage it is in, what comes next, the fidelities still open with their violations, and its latest
    log lines. The agent's own handoff, drafted from the conversation, is the ⇥ handoff action."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket

    @property
    def document(self) -> str:
        return "\n".join([self._heading, "", *self._outcome, "", *self._progress, "", *self._approach, ""])

    @property
    def _heading(self) -> str:
        today = datetime.now(timezone.utc).date().isoformat()
        return f"# Handoff — {self._ticket.title} left in {self._ticket.column.name} ({today})"

    @property
    def _next(self) -> FidelityProgress | None:
        return self._ticket.next_fidelity

    @property
    def _outcome(self) -> list[str]:
        ticket = self._ticket
        upcoming = self._next
        place = f"{ticket.name} is in {ticket.column.name}" + (", done there." if ticket.is_done else ".")
        start = f" The next session starts at {upcoming.fidelity.slug}, whose next action is {upcoming.next_action}." if upcoming else ""
        return ["## Outcome", place + start]

    @property
    def _progress(self) -> list[str]:
        open_work = [progress for progress in self._ticket.progress if progress.is_enabled and progress.stage is self._ticket.column and not progress.is_done]
        outstanding = [f"- {progress.fidelity.slug}: {progress.state}{self._violations_of(progress)}" for progress in open_work] or ["- nothing open in this stage"]
        log = [f"- {entry.text}" for entry in self._ticket.session.log.entries[-LOG_LINES_QUOTED:]] or ["- nothing logged yet"]
        return ["## Progress", "", "### Outstanding", *outstanding, "", "### Latest log", *log]

    def _violations_of(self, progress: FidelityProgress) -> str:
        count = progress.violation_count
        return f", {count} violations" if count else ""

    @property
    def _approach(self) -> list[str]:
        upcoming = self._next
        lines = ["## Approach for Next Agent", "- Read this handoff, then the session's latest validation reports."]
        if upcoming:
            lines.append(f"- Start at `{upcoming.command(upcoming.next_action)}`.")
        return lines
