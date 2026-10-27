"""SessionCompactor - compact the current session into a handoff doc via Handoff."""
from __future__ import annotations

from handoff.handoff import Handoff


class SessionCompactor:
    """Write a structured handoff document so a fresh agent can continue the session."""

    def compact(self, destination: str, focus: str) -> str:
        """Compact the current session into a handoff document under destination.

        Calls Handoff.compact_handoff, which resolves the working folder, collects
        generator and CDD state, renders the handoff template, and writes both an
        archived copy (handoffs/handoff-YYYY-MM-DD-{focus}.md) and handoff-latest.md
        at the docs root. Returns the archive path written.
        """
        handoff = Handoff()
        return handoff.compact_handoff(destination=destination, next_focus=focus)
