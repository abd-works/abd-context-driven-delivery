"""What a ticket offers a person to look at and choose on its action bars and panels: its fidelities' files, the files
under its session's folder, the format chips, and the pattern overlays."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from harness.agent_tools.agent_tools import agent_tool, noSessionLog
from harness.annotations.annotation import hosted_only
from harness.graph.pattern_overlays import PatternOverlays
from harness.mcp.mcp_annotations import long_call, mcp
from space.kanban.format_choice import FormatChoice
from space.kanban.overlay_choice import OverlayChoice
from space.session.file_manager import FileEntry

if TYPE_CHECKING:
    from space.kanban.ticket import TicketWork
    from space.session import Session


@hosted_only
class TicketChoices:
    """*TicketChoices* are the files and choices a ticket offers its board, published as its tools: each fidelity's files
    and every file under its session's folder, the format chips of an action bar over some of its fidelities, and the
    pattern overlays its session can lay on its graph. Mixed into *Ticket*, whose work and session it reads."""

    work: TicketWork
    session: Session
    forget_reads: Callable[[], None]

    @mcp
    @agent_tool
    @noSessionLog
    def fidelity_files(self, fidelities: list[str]) -> dict[str, dict[str, list[FileEntry]]]:
        """Return the files a person reviews for each of fidelities, slugs such as stories-story-map, on ticket, by slug and then by format, as each fidelity-progress.files answers them: one call for a page listing many fidelities, sharing one look at what the branch changed."""
        return {slug: self.work.progress_of(slug).files() for slug in fidelities}

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def root_files(self) -> list[FileEntry]:
        """Return every file under the folder ticket's session works in, each with its path from the project, whether the branch changed it, its format, and the fidelities whose files it is, so a page narrows it by the stages, practices, and formats selected; a file no fidelity declares names none."""
        session = self.session
        progress = self.work.progress
        repo = session.repo.root
        return [entry.belonging_to([each.fidelity.slug for each in progress if each.holds(repo / entry.path)]) for entry in session.session_files.under_root()]

    @mcp
    @agent_tool
    @noSessionLog
    def format_choices(self, fidelities: list[str]) -> list[FormatChoice]:
        """Return the format chips of an action bar on ticket over fidelities, slugs such as stories-story-map: each group of formats they offer, the format each fidelity uses from it, how many offer it and have a file in it already, and whether it is chosen for them in the session."""
        read = [(progress.fidelity, progress.files()) for progress in (self.work.progress_of(slug) for slug in fidelities)]
        return FormatChoice.offered_by(read)

    @mcp
    @agent_tool
    @noSessionLog
    def choose_formats(self, fidelities: list[str], label: str, is_chosen: bool) -> list[FormatChoice]:
        """Turn the chip label, such as markdown, on or off for fidelities, slugs such as stories-story-map, on ticket: each fidelity chooses, or leaves out, the format it uses from that group in the session, the same choice the Story UI's toggles make; return the chips again."""
        chips = self.format_choices(fidelities)
        next(chip for chip in chips if chip.label == label).choose(is_chosen)
        return self.format_choices(fidelities)

    @mcp
    @agent_tool
    @noSessionLog
    def overlay_choices(self) -> list[OverlayChoice]:
        """Return the pattern overlays a person can choose for ticket's session: every registered pattern in name order, each with its icon, its first and last letter, and whether the session overlays it on its graph."""
        chosen = self.session.overlays
        return [OverlayChoice(pattern, pattern in chosen) for pattern in PatternOverlays().names]

    @mcp
    @agent_tool
    def choose_overlays(self, overlays: list[str]) -> list[OverlayChoice]:
        """Overlay the patterns overlays names, such as lern_domain_driven, on ticket's session's graph in place of those chosen before, refusing a name that is no pattern with NotAPatternError; return its overlay choices."""
        self.session.choose_overlays(overlays)
        self.forget_reads()
        return self.overlay_choices()
