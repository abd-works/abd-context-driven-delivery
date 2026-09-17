"""Handoff - write a compact session summary so the next agent can continue.

Writes handoff-{timestamp}.md into the current session folder (.sessions/{name}/).
No archiving, no latest pointer — one timestamped file per call.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from installer.installer_tool import prompt
from workspace import SessionPaths, Workspace
from agent_tools import agent_instructions, agent_toolset
from agent_tools.agent_tools import agent_tool


@agent_toolset
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
        """Draft the handoff markdown from this conversation. Tailor it to {{next_focus}} when provided.

        Use this exact structure:

        # Handoff — {one-line description} ({today ISO date})

        ## Outcome
        One paragraph: what this session actually achieved and where the next session starts.

        ## Progress
        Keep this section terse. Do not write long essays.

        ### Files
        Short bullet list of created or modified files — relative paths plus a few words each.

        ### Outstanding
        Short bullet list of remaining work, failures, and partial items.

        ## Key Learnings
        Do not cross-check AGENTS.md or dump every learning. List only the most important rules / corrections from the corrections document: rule name + star count, optionally the session delta. One line per rule. If every learning is already in that file, the list of top rules is still required — do not write "All captured. No new items." as a substitute.

        Find the corrections document in this order:
        1. Assume it is in the current session folder (e.g. `.sessions/{name}/corrections.md` or a path the session already uses).
        2. If not found, search the sessions root (`.sessions/corrections.md`, `.sessions/**/corrections.md`).
        3. If still not found, look under `.sessions/default/`.
        4. Also try the durable project location `.context/corrections.md` if the session copies are missing.

        Read the current session block first (the latest `# Session: YYYY-MM-DD` heading). Prefer rules that appear in that block, ordered by star count.

        ## Approach for Next Agent
        Analyse the chat and/or the user's instructions for a deliberate numbered loop whose steps are context tools plus their parameters. Extract the actual slash-command / tool+parameter sequence used or instructed in this session. Do not invent a generic software process.

        Examples of the style (replace with the sequence from this session):
        - `/stories-scenarios` `/generate` `/markdown`
        - `/clean-engineering-model` `/generate` `/markdown`
        - `/stories-acceptance-tests` `/clean-engineering-code` `/generate` `/code`

        Include:
        - Read this handoff and the corrections document (session block first) to orient.
        - The numbered context-tool loop extracted from this session.
        - If a skill conflicts with corrections.md, follow corrections.md.
        - A start-at pointer for the next agent.
        - Corrections CLI commands if a `corrections-cli` exists in the project.

        ## Correction trend
        Include this section only if the corrections document was found. Compare this session's correction count (from the session block / conversation) to the previous session's count. State the trend in 1–2 sentences (e.g. "Session 2026-09-14 needed 5 corrections across 2 epics — roughly 2–3 per story. The previous session needed ~12. Trend is sharply down."). Optionally append the Corrections CLI cheat sheet (`list`, `add-correction`, `new-session`). If corrections cannot be found after the search order above, omit this section.
        """
        self.write_handoff(content="")
        """Call write_handoff(content) with the complete markdown above. Report the returned path to the user."""
        return "Handoff written."
