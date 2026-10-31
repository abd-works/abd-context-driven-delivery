"""A backlog item: an idea a person has added to the backlog folder as one markdown file."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.kanban.ticket import LOG_FILE, TIMESTAMP_FORMAT

if TYPE_CHECKING:
    from harness.kanban.board import Board
    from harness.kanban.ticket import Ticket


class BacklogItem:
    """*BacklogItem* is an idea not yet started. Starting it opens a ticket for it."""

    def __init__(self, path: Path, board: Board) -> None:
        self._path = Path(path)
        self._board = board

    @property
    def path(self) -> Path:
        return self._path

    @property
    def title(self) -> str:
        """The item's first `# ` heading, or its file name in words."""
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return self._path.stem.replace("-", " ").replace("_", " ").capitalize()

    def start(self, scope: str) -> Ticket:
        """Open a ticket for this item; the ticket's session log names the item's file."""
        ticket = self._board.new_ticket(self.title, scope, None)
        stamp = datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
        log = self._board.sessions_folder / ticket.name / LOG_FILE
        with log.open("a", encoding="utf-8") as lines:
            lines.write(f"{stamp} backlog {self._path}\n")
        return ticket

    def to_json(self) -> dict[str, Any]:
        return {"title": self.title, "path": str(self._path)}
