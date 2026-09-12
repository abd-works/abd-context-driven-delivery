# @toolset-manifest python -m tools manifest handoff.handoff:Handoff
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Handoff - write a compact session summary so the next agent can continue.

Writes handoff-{timestamp}.md into the current session folder (.sessions/{name}/).
No archiving, no latest pointer — one timestamped file per call.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from harness.harness_tool import prompt
from workspace import SessionPaths, Workspace
from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool


@agentic_toolset
class Handoff:
    """Write a compact session handoff for the next agent."""

    def __init__(self, path: str = ".", workspace: str = "", session: str = "") -> None:
        root = workspace or path
        self.workspace = Workspace(str(root))
        self.workspace.load()
        if session:
            self.workspace.open(name=session, path=root)

    def _session_folder(self) -> Path:
        """Current active session folder; falls back to the most-recently-modified
        session dir, then .sessions/session/ when none exist."""
        active = self.workspace.current_work_session
        if active is not None:
            return active.folder
        sessions = SessionPaths.sessions_root(self.workspace.path)
        if sessions.is_dir():
            candidates = [p for p in sessions.iterdir() if p.is_dir() and p.name != "closed"]
            if candidates:
                return max(candidates, key=lambda p: p.stat().st_mtime)
        fallback = sessions / "session"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

    @agent_tool
    def write_handoff(self, content: str) -> str:
        """Write content to the current session folder as handoff-{timestamp}.md.
        Returns the absolute path of the written file."""
        folder = self._session_folder()
        folder.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = folder / f"handoff-{ts}.md"
        path.write_text(content, encoding="utf-8")
        return str(path.resolve())

    @prompt
    @agent_instructions
    def handoff_session(self, next_focus: str = "") -> str:
        """Write a compact handoff for the current session so the next agent can continue. Tailor to {{next_focus}} when provided."""
        """Draft the handoff markdown from this conversation — no file lookups needed.

        Use this exact structure:

        # Handoff — {one-line description} ({today ISO date})

        ## Outcome
        One paragraph: what was actually achieved this session.

        ## Progress
        ### Files
        Bullet list of every file created or modified, with relative paths.

        ## Outstanding
        Bullet list of remaining work, failures, partial items, and corrections not yet applied.

        ## Key Learnings
        Cross-check every candidate learning against AGENTS.md files visible in the conversation.
        List only learnings NOT already recorded there, or ones whose wording needs updating.
        If every learning is already captured, say so explicitly.

        ## Approach for Next Agent
        The exact loop or steps the next agent must follow.
        Include exact /commands, skill names (e.g. /render stories-scenarios), and a numbered checklist.
        """
        self.write_handoff(content="")
        """Call write_handoff(content) with the complete markdown above. Report the returned path to the user."""
        return "Handoff written."
