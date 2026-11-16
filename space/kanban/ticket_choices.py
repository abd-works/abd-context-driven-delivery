"""What a ticket offers a person to look at and choose on its action bars and panels: its fidelities' files, the files
under its session's folder, the format chips, and the pattern overlays."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.pattern_overlays import PatternOverlays
from space.kanban.format_choice import FormatChoice
from space.kanban.overlay_choice import OverlayChoice
from space.session.file_manager import FileEntry

if TYPE_CHECKING:
    from space.kanban.ticket import Ticket


class TicketChoices:
    """*TicketChoices* are the files and choices one ticket offers its board: each fidelity's files and every file under
    its session's folder, the format chips of an action bar over some of its fidelities, and the pattern overlays its
    session can lay on its graph."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket

    def fidelity_files(self, fidelities: list[str]) -> dict[str, dict[str, list[FileEntry]]]:
        """The files of each of fidelities, by slug and then by format."""
        return {slug: self._ticket.work.progress_of(slug).files() for slug in fidelities}

    def root_files(self) -> list[FileEntry]:
        """Every file under the folder the ticket's session works in, each naming the fidelities whose files it is."""
        session = self._ticket.session
        progress = self._ticket.work.progress
        repo = session.repo.root
        return [entry.belonging_to([each.fidelity.slug for each in progress if each.holds(repo / entry.path)]) for entry in session.session_files.under_root()]

    def format_choices(self, fidelities: list[str]) -> list[FormatChoice]:
        """The format chips of an action bar over fidelities."""
        read = [(progress.fidelity, progress.files()) for progress in (self._ticket.work.progress_of(slug) for slug in fidelities)]
        return FormatChoice.offered_by(read)

    def choose_formats(self, fidelities: list[str], label: str, is_chosen: bool) -> list[FormatChoice]:
        """The chip label turned on or off for fidelities, and the chips again."""
        chips = self.format_choices(fidelities)
        next(chip for chip in chips if chip.label == label).choose(is_chosen)
        return self.format_choices(fidelities)

    def overlay_choices(self) -> list[OverlayChoice]:
        """Every registered pattern in name order, each with whether the session overlays it on its graph."""
        chosen = self._ticket.session.overlays
        return [OverlayChoice(pattern, pattern in chosen) for pattern in PatternOverlays().names]

    def choose_overlays(self, overlays: list[str]) -> list[OverlayChoice]:
        """The patterns overlays names laid on the session's graph in place of those chosen before, and the choices again."""
        self._ticket.session.choose_overlays(overlays)
        self._ticket.forget_reads()
        return self.overlay_choices()
