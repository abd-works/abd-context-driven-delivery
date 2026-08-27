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
from harness.harness_tool import prompt
from primitives.actions.action import agent_instructions
from tools.tool import agent_tool, toolset
from workspace import Workspace
from workspace.git_repo import NullGitRepo


_PROJECT_STATUSES = ("Backlog", "In Progress", "Done")


@dataclass(frozen=True)
class WorkflowConfig:
    project_owner: str
    project_number: int
    default_branch: str = "main"


@toolset
class Workflow:
    """Slash /backlog, /start-ticket, /finish-ticket — GitHub issue + session lifecycle."""

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

    @prompt(name="backlog")
    @agent_instructions
    def backlog(self, focus: str, context: str = "", workspace: str = "") -> str:
        """Capture an idea on the backlog — GitHub issue + Project Backlog."""
        self._handoff().handoff_session()
        """Call `capture_backlog` with the handoff markdown as the issue body, not a file path."""
        self.capture_backlog()
        return "Backlog captured — GitHub issue created in Project Backlog."

    @agent_tool
    def capture_backlog(
        self, focus: str, body: str, workspace: str = ""
    ) -> dict[str, str | int]:
        """Create a GitHub issue whose body is the handoff text, Project Backlog."""
        issue_body = self._handoff_issue_body(body)
        return self.create_ticket(
            title=focus.strip() or "backlog",
            body=issue_body,
            workspace=workspace,
            project_status="Backlog",
        )

    def _handoff_issue_body(self, body: str) -> str:
        text = body.strip()
        path = Path(text)
        if text and path.is_file():
            text = path.read_text(encoding="utf-8")
        return text

    @prompt(name="start-ticket")
    @agent_tool
    def start(
        self,
        ticket: str,
        instructions: str = "",
        workspace: str = "",
        copy_body: bool = False,
        workflow_state: str = "specification",
    ) -> dict[str, str | int]:
        """Start work from a GitHub issue — In Progress, WorkSession, session branch."""
        viewed = self.view_ticket(ticket, workspace=workspace)
        self.set_ticket_project_status(ticket, "In Progress", workspace=workspace)
        opened = self.open_ticket_session(
            ticket,
            instructions=instructions,
            workspace=workspace,
            workflow_state=workflow_state,
        )
        if copy_body:
            self.copy_issue_body_to_session(
                ticket, str(opened["session_name"]), workspace=workspace
            )
        ws = self._workspace(workspace)
        session = ws.current_work_session
        if session is not None and session.open_turn is not None:
            message = self.turn_commit_message(
                subject=f"start {session.name}",
                ticket=ticket,
                workflow_state=workflow_state,
                workspace=workspace,
            )
            session.open_turn.finish(
                prompt=instructions,
                result=message,
                context=session.name,
            )
        if session is not None:
            session.git.checkout_or_create(session.session_branch)
        return {**viewed, **opened}

    @prompt(name="finish-ticket")
    @agent_tool
    def finish(
        self,
        outcome: str = "",
        workspace: str = "",
        ticket: str = "",
        reviewed_by: str = "",
    ) -> dict[str, str]:
        """Finish the open WorkSession — merge to main, Done, close issue, close session."""
        session_name = self.require_open_session(workspace=workspace)
        ws = self._workspace(workspace)
        session = ws.current_work_session
        if session is not None and session.open_turn is not None:
            session.open_turn.finish(
                prompt=outcome,
                result="finish",
                context=session_name,
            )
        sha = self.merge_session_to_main(
            workspace=workspace, ticket=ticket, reviewed_by=reviewed_by
        )
        if ticket.strip():
            self.set_ticket_project_status(ticket, "Done", workspace=workspace)
            self.close_ticket(ticket, workspace=workspace)
        if outcome.strip() and session is not None:
            session.close_session(outcome=outcome)
        return {"commit": sha, "session_name": session_name}

    def _handoff(self) -> Handoff:
        return Handoff()

    def workspace_tool(self, path: str = "") -> Workspace:
        return self._workspace(path)

    def load_project_config(self, workspace: str = "") -> dict[str, str | int]:
        repo_root = self._repo_root(workspace)
        config = self._load_workflow_config(repo_root)
        return {
            "project_owner": config.project_owner,
            "project_number": config.project_number,
            "default_branch": config.default_branch,
        }

    def parse_ticket(self, ticket: str) -> int:
        return Ticket.parse_number(ticket)

    def session_name_for_issue(self, title: str, number: int) -> str:
        return self._session_name_from_issue(title, number)

    def turn_commit_message(
        self,
        subject: str,
        ticket: str,
        workflow_state: str,
        workspace: str = "",
        reviewed_by: str = "",
    ) -> str:
        repo = self._repo(workspace)
        return repo.workflow_commit_message(
            subject,
            Ticket.parse_number(ticket),
            workflow_state,
            reviewed_by=reviewed_by,
        )

    def view_ticket(self, ticket: str, workspace: str = "") -> dict[str, str | int]:
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

    def create_ticket(
        self,
        title: str,
        body: str,
        workspace: str = "",
        project_status: str = "Backlog",
    ) -> dict[str, str | int]:
        if project_status not in _PROJECT_STATUSES:
            raise ValueError(f"project_status must be one of {_PROJECT_STATUSES}")
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        self._ensure_project(repo, repo_root)
        ticket = repo.create_ticket(title, body)
        ticket.set_status(project_status)
        return {
            "number": ticket.number,
            "title": ticket.title,
            "body": ticket.body,
            "url": ticket.url,
            "project_status": project_status,
        }

    def set_ticket_project_status(
        self,
        ticket: str,
        status: str,
        workspace: str = "",
    ) -> str:
        if status not in _PROJECT_STATUSES:
            raise ValueError(f"status must be one of {_PROJECT_STATUSES}")
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        issue = repo.ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        self._ensure_project(repo, repo_root)
        issue.set_status(status)
        return status

    def copy_issue_body_to_session(
        self,
        ticket: str,
        session_name: str,
        workspace: str = "",
        filename: str = "issue-body.md",
    ) -> str:
        repo_root = self._repo_root(workspace)
        issue = self._repo(workspace).ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        session_folder = repo_root / ".context" / "sessions" / session_name
        session_folder.mkdir(parents=True, exist_ok=True)
        target = session_folder / filename
        target.write_text(issue.body, encoding="utf-8")
        return str(target.resolve())

    def open_ticket_session(
        self,
        ticket: str,
        instructions: str = "",
        workspace: str = "",
        workflow_state: str = "specification",
    ) -> dict[str, str]:
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
        open_turn = session.turn
        open_turn.action = "start"
        if instructions.strip():
            open_turn.prompt = instructions.strip()
        return {
            "session_name": session.name,
            "branch": session.session_branch,
            "issue_number": str(issue.number),
            "issue_url": issue.url,
            "workflow_state": workflow_state,
        }

    def require_open_session(self, workspace: str = "") -> str:
        ws = self._workspace(workspace)
        session = ws.current_work_session
        if session is None:
            branch = self._repo(workspace).current_branch
            if isinstance(branch, str) and branch.startswith("session/"):
                ws.open(
                    name=branch[len("session/") :],
                    path=str(self._repo_root(workspace)),
                )
                session = ws.current_work_session
        if session is None:
            raise RuntimeError("no open work session")
        return session.name

    def merge_session_to_main(
        self,
        workspace: str = "",
        ticket: str = "",
        reviewed_by: str = "",
    ) -> str:
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

    def close_ticket(self, ticket: str, workspace: str = "") -> str:
        issue = self._repo(workspace).ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        issue.close()
        return f"closed {ticket}"
