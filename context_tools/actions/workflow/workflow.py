# @toolset-manifest python -m tools manifest workflow.workflow:Workflow
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Workflow — backlog, start, finish linking GitHub Issues, handoff, and WorkSession."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from git import Ticket, TicketNotFoundError
from git.git import Repo
from handoff.handoff import Handoff
from primitives.actions.action import agent_instructions
from tools.tool import agent_tool, toolset
from workspace import Workspace
from workspace.git_repo import NullGitRepo
from workspace.workspace import ContextToolHost, Turn


_PROJECT_STATUSES = ("Backlog", "In Progress", "Done")


@dataclass(frozen=True)
class WorkflowConfig:
    project_owner: str
    project_number: int
    default_branch: str = "main"


@toolset
class Workflow:
    """Slash /backlog, /start, /finish — GitHub issue + session lifecycle (v1 simple)."""

    def __init__(
        self,
        workspace: str = "",
        *,
        repo: Repo | None = None,
    ) -> None:
        self._workspace_path = workspace.strip()
        self._repo_override = repo
        self._workspaces: dict[str, Workspace] = {}

    def _repo_root(self, workspace: str = "") -> Path:
        start = workspace.strip() or self._workspace_path or "."
        root = Repo.find_root(start)
        if root is None:
            raise ValueError(f"not a git clone: {start!r}")
        return root

    def _repo(self, workspace: str = "") -> Repo:
        if self._repo_override is not None:
            return self._repo_override
        return Repo.open(self._repo_root(workspace))

    def _workspace(self, workspace: str = "") -> Workspace:
        root = str(self._repo_root(workspace))
        cached = self._workspaces.get(root)
        if cached is not None:
            return cached
        ws = Workspace(root)
        ws.load()
        self._workspaces[root] = ws
        return ws

    def _kebab(self, text: str) -> str:
        cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in text.strip())
        while "--" in cleaned:
            cleaned = cleaned.replace("--", "-")
        return cleaned.strip("-") or "idea"

    def _session_name_from_issue(self, title: str, number: int) -> str:
        slug = self._kebab(title)
        return f"{slug}-{number}" if slug else f"issue-{number}"

    def _workflow_config_path(self, repo_root: Path) -> Path:
        return repo_root / ".context" / "workflow.yaml"

    def _load_workflow_config(self, repo_root: Path) -> WorkflowConfig:
        path = self._workflow_config_path(repo_root)
        if not path.is_file():
            raise FileNotFoundError(
                f"missing workflow config: {path.as_posix()} "
                "(need project_owner and project_number)"
            )
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        owner = str(payload.get("project_owner") or "").strip()
        number = payload.get("project_number")
        if not owner or number is None:
            raise ValueError(
                "workflow.yaml requires project_owner and project_number"
            )
        return WorkflowConfig(
            project_owner=owner,
            project_number=int(number),
            default_branch=str(payload.get("default_branch") or "main").strip()
            or "main",
        )

    def _ensure_project(self, repo: Repo, repo_root: Path):
        if repo.project is not None:
            return repo.project
        config = self._load_workflow_config(repo_root)
        return repo.attach_project(config.project_owner, config.project_number)

    @agent_tool
    def handoff_tool(self) -> Handoff:
        """Handoff toolset — use content/collection patterns when composing issue body text."""
        return Handoff()

    @agent_tool
    def workspace_tool(self, path: str = "") -> Workspace:
        """Workspace aggregate for open_work_session (path defaults to repo root)."""
        return self._workspace(path)

    @agent_tool
    def load_project_config(self, workspace: str = "") -> dict[str, str | int]:
        """Read `.context/workflow.yaml` for GitHub Project owner/number."""
        repo_root = self._repo_root(workspace)
        config = self._load_workflow_config(repo_root)
        return {
            "project_owner": config.project_owner,
            "project_number": config.project_number,
            "default_branch": config.default_branch,
        }

    @agent_tool
    def parse_ticket(self, ticket: str) -> int:
        """Normalize a GitHub issue reference to its issue number."""
        return Ticket.parse_number(ticket)

    @agent_tool
    def session_name_for_issue(self, title: str, number: int) -> str:
        """Build the work-session slug from an issue title and number."""
        return self._session_name_from_issue(title, number)

    @agent_tool
    def turn_commit_message(
        self,
        subject: str,
        ticket: str,
        workflow_state: str,
        workspace: str = "",
        reviewed_by: str = "",
    ) -> str:
        """Format a turn or merge commit message with workflow trailers."""
        repo = self._repo(workspace)
        return repo.workflow_commit_message(
            subject,
            Ticket.parse_number(ticket),
            workflow_state,
            reviewed_by=reviewed_by,
        )

    @agent_tool
    def view_ticket(self, ticket: str, workspace: str = "") -> dict[str, str | int]:
        """Load a GitHub issue via gh; raises when the ticket is not found."""
        repo = self._repo(workspace)
        issue = repo.ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "url": issue.url,
        }

    @agent_tool
    def create_ticket(
        self,
        title: str,
        body: str,
        workspace: str = "",
        project_status: str = "Backlog",
    ) -> dict[str, str | int]:
        """Create a GitHub issue and add it to the repository Project."""
        if project_status not in _PROJECT_STATUSES:
            raise ValueError(f"project_status must be one of {_PROJECT_STATUSES}")
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        project = self._ensure_project(repo, repo_root)
        ticket = repo.create_ticket(title=title, body=body)
        project.add_ticket(ticket, project_status)
        return {
            "number": ticket.number,
            "title": ticket.title,
            "body": ticket.body,
            "url": ticket.url,
            "project_status": project_status,
        }

    @agent_tool
    def set_ticket_project_status(
        self,
        ticket: str,
        status: str,
        workspace: str = "",
    ) -> str:
        """Move an issue to Backlog, In Progress, or Done on the repo Project."""
        if status not in _PROJECT_STATUSES:
            raise ValueError(f"status must be one of {_PROJECT_STATUSES}")
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        issue = repo.ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        project = self._ensure_project(repo, repo_root)
        project.set_ticket_state(issue, status)
        return status

    @agent_tool
    def copy_issue_body_to_session(
        self,
        ticket: str,
        session_name: str,
        workspace: str = "",
        filename: str = "issue-body.md",
    ) -> str:
        """Copy the GitHub issue body into the work session folder when local artifacts help."""
        repo_root = self._repo_root(workspace)
        issue = self._repo(workspace).ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        session_folder = repo_root / ".context" / "sessions" / session_name
        session_folder.mkdir(parents=True, exist_ok=True)
        target = session_folder / filename
        target.write_text(issue.body, encoding="utf-8")
        return str(target.resolve())

    @agent_tool
    def open_ticket_session(
        self,
        ticket: str,
        instructions: str = "",
        workspace: str = "",
        workflow_state: str = "specification",
    ) -> dict[str, str]:
        """Open a WorkSession for a GitHub issue and return session metadata."""
        repo_root = self._repo_root(workspace)
        issue = self._repo(workspace).ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        session_name = self._session_name_from_issue(issue.title, issue.number)
        ws = self._workspace(workspace)
        git = NullGitRepo(repo_root) if self._repo_override is not None else None
        goal = instructions.strip() or issue.title
        session = ws.open_work_session(
            name=session_name,
            goal=goal,
            path=str(repo_root),
            git=git,
        )
        host = ContextToolHost(ws, git=session.git)
        turn = Turn()
        open_turn = turn.open(host, action="start")
        if instructions.strip():
            open_turn.prompt = instructions.strip()
        return {
            "session_name": session.name,
            "branch": session.session_branch,
            "issue_number": str(issue.number),
            "issue_url": issue.url,
            "workflow_state": workflow_state,
        }

    @agent_tool
    def require_open_session(self, workspace: str = "") -> str:
        """Return the current work session name or raise when none is open."""
        session = self._workspace(workspace).current_work_session
        if session is None:
            raise RuntimeError("no open work session")
        return session.name

    @agent_tool
    def merge_session_to_main(
        self,
        workspace: str = "",
        ticket: str = "",
        reviewed_by: str = "",
    ) -> str:
        """Merge the open session branch into main with workflow trailers on the merge commit."""
        ws = self._workspace(workspace)
        session = ws.current_work_session
        if session is None:
            raise RuntimeError("no open work session")
        if session.dirty:
            raise RuntimeError("working tree is dirty")
        config = self._load_workflow_config(self._repo_root(workspace))
        source = session.session_branch
        subject = f"finish {session.name}"
        message = subject
        if ticket.strip():
            message = self._repo(workspace).workflow_commit_message(
                subject,
                Ticket.parse_number(ticket),
                "done",
                reviewed_by=reviewed_by,
            )
        session.git.merge_branch(source, config.default_branch, message=message)
        return session.git.current_commit

    @agent_tool
    def close_ticket(self, ticket: str, workspace: str = "") -> str:
        """Close the linked GitHub issue."""
        self._repo(workspace).close_ticket(ticket)
        return f"closed {ticket}"

    @agent_instructions
    def backlog(self, focus: str, context: str = "") -> str:
        """Capture an idea on the backlog — no open WorkSession; no local repo artifacts v1."""
        """1. Read `.context/research/git-knowledge-and-workflow-backbone.md` §8 if ticket/github behavior is unclear."""
        """2. Call `handoff_tool().collect_session_state(...)` and compose the backlog handoff from current fidelity, format, action, session artifacts, and prompt commentary — do not invent requirements."""
        """3. Call `create_ticket(title=..., body=..., project_status="Backlog")` using the composed handoff as the issue body (canonical; no local backlog folder v1)."""
        """4. Do not call `open_ticket_session` or `workspace_tool().open_work_session` — backlog is ticket-only v1."""
        return f"Backlog captured for {focus!r} — GitHub issue created in Project Backlog."

    @agent_instructions
    def start(self, ticket: str, instructions: str = "", workspace: str = "") -> str:
        """Start work from a GitHub issue — opens WorkSession + session branch."""
        """1. Call `view_ticket(ticket)` — if not found, stop and report not found; do not open a work session."""
        """2. Read the returned body for forward requirements; merge with `instructions` from the prompt."""
        """3. Refer to the issue as agent context when body is sufficient; call `copy_issue_body_to_session` when local artifacts help."""
        """4. Call `set_ticket_project_status(ticket, "In Progress")`."""
        """5. Call `open_ticket_session(ticket, instructions=..., workflow_state="specification" or "engineering")` — branch and dirty-tree policy are workspace scope."""
        """6. Finish the open turn with `turn_commit_message(...)` trailers: `GitHub-Issue`, `Workflow-State`. Record prompt instructions on the turn envelope."""
        return f"Started work session for GitHub issue {ticket!r}."

    @agent_instructions
    def finish(self, outcome: str = "", workspace: str = "", ticket: str = "", reviewed_by: str = "") -> str:
        """Finish current WorkSession — merge session branch to main, close issue, close session."""
        """1. Call `require_open_session(workspace=...)` — refuse when none is open."""
        """2. Finish the open turn for the action before merge."""
        """3. Call `merge_session_to_main(workspace=..., ticket=..., reviewed_by=...)` — refuse when dirty; direct merge to main v1."""
        """4. Call `set_ticket_project_status(ticket, "Done")` then `close_ticket(ticket)`."""
        """5. Checkout main is handled by merge; call `workspace_tool().current_work_session.close_session(outcome=...)` when outcome is provided."""
        return "Work session finished — merged to main, issue closed, checked out main."
