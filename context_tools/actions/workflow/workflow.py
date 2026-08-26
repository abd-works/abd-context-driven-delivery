# @toolset-manifest python -m tools manifest workflow.workflow:Workflow
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Workflow — backlog, start, finish linking GitHub Issues, handoff, and WorkSession."""
from __future__ import annotations

import json
from pathlib import Path

from handoff.handoff import Handoff
from primitives.actions.action import agent_instructions
from tools.tool import agent_tool, toolset
from workspace import Workspace, docs_dir, find_git_root

_TICKETS_DIR = ".context/workflow"
_TICKETS_INDEX = "tickets.jsonl"
_BACKLOG_SESSIONS = ".context/sessions/backlog"


@toolset
class Workflow:
    """Slash /backlog, /start, /finish — ticket + session lifecycle (v1 simple)."""

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

    def _tickets_index_path(self) -> Path:
        return self._repo_root() / _TICKETS_DIR / _TICKETS_INDEX

    def _append_ticket_record(self, record: dict) -> None:
        path = self._tickets_index_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    @agent_tool
    def backlog_destination(self, focus: str) -> str:
        """Resolve backlog handoff folder: {repo}/.context/sessions/backlog/{focus-slug}/.
        Creates parents. Returns absolute path."""
        slug = self._kebab(focus)
        dest = self._repo_root() / _BACKLOG_SESSIONS / slug
        docs_dir(str(dest)).mkdir(parents=True, exist_ok=True)
        return str(dest.resolve())

    @agent_tool
    def next_ticket_id(self) -> str:
        """Return next CDD-N ticket id from tickets.jsonl (1-based counter)."""
        path = self._tickets_index_path()
        if not path.is_file():
            return "CDD-1"
        count = sum(1 for _ in path.open(encoding="utf-8") if _.strip())
        return f"CDD-{count + 1}"

    @agent_tool
    def record_ticket(
        self,
        ticket: str,
        focus: str,
        handoff_path: str = "",
        github_issue: str = "",
    ) -> str:
        """Append a ticket record to .context/workflow/tickets.jsonl. Returns ticket id."""
        record = {
            "ticket": ticket.strip(),
            "focus": focus.strip(),
            "handoff_path": handoff_path.strip(),
            "github_issue": github_issue.strip(),
            "workflow_state": "backlog",
        }
        self._append_ticket_record(record)
        return ticket.strip()

    @agent_tool
    def find_ticket(self, ref: str) -> str:
        """Look up ticket by CDD-N or GitHub issue number. Returns JSON or empty object."""
        ref = ref.strip().lstrip("#")
        path = self._tickets_index_path()
        if not path.is_file():
            return "{}"
        matches: list[dict] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            ticket = str(row.get("ticket", ""))
            gh = str(row.get("github_issue", ""))
            if ref == ticket or ref == ticket.replace("CDD-", "") or ref in gh:
                matches.append(row)
        if not matches:
            return "{}"
        return json.dumps(matches[-1], indent=2)

    @agent_tool
    def handoff_tool(self) -> Handoff:
        """Handoff toolset for write_handoff / compact_handoff."""
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
        """Capture an idea on the backlog — no open WorkSession required."""
        """1. Read `.context/research/git-knowledge-and-workflow-backbone.md` §8 if ticket/github behavior is unclear."""
        """2. Call `next_ticket_id` then `backlog_destination` with a short focus label from the user prompt."""
        """3. Draft a handoff markdown focused on **what is required to move this idea forward** — use prompt context and commentary verbatim where useful; do not invent requirements."""
        """4. Call `handoff_tool().write_handoff(destination, content, focus=focus)` for that backlog folder."""
        """5. When a GitHub remote exists: `gh issue create --title "..." --body "..."` including Ticket id, handoff path, and forward-requirements summary; capture `owner/repo#num`."""
        """6. Call `record_ticket` with ticket id, focus, handoff path, and github_issue when created."""
        """7. Commit on current branch with trailers: `Ticket:`, `GitHub-Issue:` (if any), `Workflow-State: backlog`, `Handoff:` path. Message subject: `workflow-backlog-{focus-slug}`."""
        return f"Backlog captured for {focus!r}. Ticket + handoff + GitHub issue (when remote) recorded."

    @agent_instructions
    def start(self, ticket: str, instructions: str = "", workspace: str = "") -> str:
        """Start work from a backlog ticket — opens WorkSession + session branch."""
        """1. Call `find_ticket` with the ticket ref (CDD-N or GitHub #). If `{}`, stop and report not found."""
        """2. Read handoff at `handoff_path` from the ticket record; merge with `instructions` from the prompt."""
        """3. Call `workspace_tool(path=workspace)`. `open_work_session(name=session-slug-from-ticket, goal=..., contexts=..., fidelities=...)` — session slug = kebab focus or ticket id lowercased."""
        """4. Workspace creates/checks out `session/{name}` branch (refuses if dirty tree on another branch)."""
        """5. Open and finish a turn recording `Ticket:`, `GitHub-Issue:`, `Workflow-State: specification`, prompt/result with merged instructions."""
        return f"Started work session for ticket {ticket!r}."

    @agent_instructions
    def finish(self, outcome: str = "", workspace: str = "") -> str:
        """Finish current WorkSession — merge session branch to main, checkout main, close session."""
        """1. Require `workspace.current_work_session` on its `session/{name}` branch."""
        """2. Refuse if working tree is dirty."""
        """3. Finish open turn; merge session branch into `main` (v1 direct merge — no PR gate unless user asks)."""
        """4. Checkout `main`; close session with outcome; commit/merge trailers include `Workflow-State: done`."""
        return "Work session finished — merged to main and checked out main."
