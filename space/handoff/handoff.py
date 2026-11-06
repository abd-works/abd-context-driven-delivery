"""Handoff - write a compact session summary so the next agent can continue.

Writes handoff-{timestamp}.md into the folder of the session the handoff is for: the session a call
names, such as a board ticket's, else the current session of the project the calling chat works on,
else ``.sessions/main/`` when that project has no named current session.
No archiving, no latest pointer — one timestamped file per call.
"""
from __future__ import annotations

from harness.agent_tools import agent_instructions, agent_toolset, tools
from harness.guidance_actions import load_document
from harness.agent_tools.agent_tools import agent_tool, tool_subject
from harness.installation.destination import noCatalog
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp
from space.repo.repo import Repo
from space.session.session import Session

@noCatalog
@agent_toolset
class Handoff:
    """Write a compact session handoff for the next agent."""

    _session: Session | None = None

    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    @classmethod
    @tool_subject
    def for_session(cls, session: str = "") -> Handoff:
        """The handoff for the session called session, such as the board ticket a handoff is asked for; the current
        session of the project the call names when it names none. A chat can be asked for another ticket's handoff, so
        the name decides the folder, never whichever session that chat has open."""
        return cls(Repo.current().session_named(session) if session else None)

    def _session_or_current(self) -> Session:
        """The session this handoff is written into. A method rather than a property, so the toolset does not offer the session's own tools as its
        own."""
        return self._session or Session.current()

    @mcp
    @skill
    @agent_tool
    def write_handoff(self, content: str = "", paths: list[str] | str | None = None) -> str:
        """Write a handoff into the session's folder, .sessions/{session}/handoff-{timestamp}.md: the session named by session, else the current session (.sessions/main/ with no named session).
        Returns the absolute path of the written file.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the handoff body in content.
        content: in-process text. Leave this empty on an MCP call."""
        document = load_document(content, paths)
        if not document.strip():
            return "Nothing written: draft the handoff to a file and pass its path in paths."
        path = self._session_or_current().new_handoff_path()
        path.write_text(document, encoding="utf-8")
        return str(path.resolve())

    @mcp
    @skill
    @agent_instructions
    def handoff_session(self, next_focus: str = "", session: str = "") -> str:
        """Write a compact handoff for session {{session}} (the current session when blank) so the next agent can continue. Tailor to {{next_focus}} when provided."""
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
        3. If still not found, look under `.sessions/main/`.
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
        tools(self.write_handoff)
        """Write the handoff markdown to a file and call write_handoff with paths set to that file and session set to {{session}}; leave session empty when it is blank, so the handoff goes to the current session. Do not pass the handoff body. Report the returned path to the user."""
        return "Handoff written."
