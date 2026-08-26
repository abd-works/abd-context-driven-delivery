# @toolset-manifest python -m tools manifest workflow.workflow:Workflow
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Workflow — backlog, start, finish linking GitHub Issues, handoff, and WorkSession."""
from __future__ import annotations

from pathlib import Path

from handoff.handoff import Handoff
from primitives.actions.action import agent_instructions
from tools.tool import agent_tool, toolset
from workspace import Workspace, find_git_root


@toolset
class Workflow:
    """Slash /backlog, /start, /finish — GitHub issue + session lifecycle (v1 simple)."""

    def __init__(self, workspace: str = "") -> None:
        self._workspace_path = workspace.strip()

    def _repo_root(self) -> Path:
        start = self._workspace_path or "."
        root = find_git_root(start)
        if root is None:
            raise ValueError(f"not a git clone: {start!r}")
        return root

    def _kebab(self, text: str) -> str:
        cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in text.strip())
        while "--" in cleaned:
            cleaned = cleaned.replace("--", "-")
        return cleaned.strip("-") or "idea"

    @agent_tool
    def handoff_tool(self) -> Handoff:
        """Handoff toolset — use content/collection patterns when composing issue body text."""
        return Handoff()

    @agent_tool
    def workspace_tool(self, path: str = "") -> Workspace:
        """Workspace aggregate for open_work_session (path defaults to repo root)."""
        root = find_git_root(path or self._workspace_path or ".")
        if root is None:
            raise ValueError("not a git clone")
        return Workspace(str(root))

    @agent_instructions
    def backlog(self, focus: str, context: str = "") -> str:
        """Capture an idea on the backlog — no open WorkSession; no local repo artifacts v1."""
        """1. Read `.context/research/git-knowledge-and-workflow-backbone.md` §8 if ticket/github behavior is unclear."""
        """2. Draft **issue body** forward-requirements from prompt context and commentary — use handoff content patterns; do not invent requirements."""
        """3. `gh issue create --title "..." --body "..."` with that body as the canonical handoff."""
        """4. Add issue to the repository Project: `gh project item-add` then `gh project item-edit --field Status --value "Backlog"`."""
        """5. Do not open a WorkSession; do not write a local backlog folder for v1."""
        return f"Backlog captured for {focus!r} — GitHub issue created in Project Backlog."

    @agent_instructions
    def start(self, ticket: str, instructions: str = "", workspace: str = "") -> str:
        """Start work from a GitHub issue — opens WorkSession + session branch."""
        """1. `gh issue view {ticket}` — if not found, stop and report not found."""
        """2. Read issue body for forward requirements; merge with `instructions` from the prompt."""
        """3. Refer to the issue as agent context when body is sufficient; copy sections into the work session folder when local artifacts help."""
        """4. Set Project Status **In Progress** via `gh project item-edit`."""
        """5. Call `workspace_tool(path=workspace)`. `open_work_session(name=session-slug-from-issue, goal=..., contexts=..., fidelities=...)` — session slug = kebab from issue title or focus."""
        """6. Workspace creates/checks out `session/{name}` branch (refuses if dirty tree on another branch)."""
        """7. Open and finish a turn with commit trailers: `GitHub-Issue: owner/repo#num`, `Workflow-State: specification` (or `engineering`). Record prompt instructions on the turn envelope."""
        return f"Started work session for GitHub issue {ticket!r}."

    @agent_instructions
    def finish(self, outcome: str = "", workspace: str = "") -> str:
        """Finish current WorkSession — merge session branch to main, close issue, close session."""
        """1. Require `workspace.current_work_session` on its `session/{name}` branch."""
        """2. Refuse if working tree is dirty."""
        """3. Finish open turn; merge session branch into `main` (v1 direct merge — no PR gate unless user asks)."""
        """4. Set Project Status **Done**; `gh issue close` for the linked issue (no PR auto-close in v1)."""
        """5. Checkout `main`; close session with outcome; merge commit trailers: `GitHub-Issue:`, `Workflow-State: done`, optional `Reviewed-By:`."""
        return "Work session finished — merged to main, issue closed, checked out main."
