# @toolset-manifest python -m tools manifest workflow.workflow:Workflow
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Workflow — backlog, start, finish linking GitHub Issues, handoff, and WorkSession."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from git import Ticket, TicketNotFoundError
from git.git import Repo
from handoff.handoff import Handoff
from harness.harness_tool import prompt
from tools.tool import agent_tool, toolset
from workflow.work_ticket import WorkTicket
from workspace import Workspace
from workspace.git_repo import NullGitRepo


_PROJECT_STATUSES = ("Backlog", "In Progress", "Done")


@dataclass(frozen=True)
class WorkflowConfig:
    project_owner: str
    project_number: int
    default_branch: str = "main"


@dataclass
class FlowFile:
    """Per-state behavior for a Workflow — ``workflow/flows/{name}.yaml``.

    Columns stay on the GitHub Project; this file holds tools, one action,
    utilities, prose, optional hil/judge, and owner + project_number.
    """

    name: str
    owner: str | None = None
    project_number: int | None = None
    throwaway: bool = False
    states: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "FlowFile":
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls(
            name=str(payload.get("name") or path.stem),
            owner=(str(payload["owner"]).strip() if payload.get("owner") else None),
            project_number=(
                int(payload["project_number"])
                if payload.get("project_number") is not None
                else None
            ),
            throwaway=bool(payload.get("throwaway", False)),
            states=dict(payload.get("states") or {}),
        )

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {
            "name": self.name,
            "throwaway": self.throwaway,
            "states": self.states or {},
        }
        if self.owner:
            payload["owner"] = self.owner
        if self.project_number is not None:
            payload["project_number"] = self.project_number
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


@toolset
class Workflow:
    """Slash /backlog, /start-ticket, /finish-ticket, /finish-plan — kit + board (no Actions)."""

    def __init__(
        self,
        workspace: str = "",
        *,
        repo: Repo | None = None,
        name: str = "",
        throwaway: bool = False,
        flow_project_number: int | None = None,
    ) -> None:
        self._workspace_path = workspace.strip()
        self._repo_override = repo
        self._workspaces: dict[str, Workspace] = {}
        self.name = name.strip()
        self.throwaway = throwaway
        self.flow_project_number = flow_project_number
        self.flow_file_path: Path | None = None
        if self.name:
            root = Path(self._workspace_path or ".")
            self.flow_file_path = root / "workflow" / "flows" / f"{self.name}.yaml"

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
    @agent_tool
    def backlog(
        self,
        focus: str,
        context: str = "",
        workspace: str = "",
        theme: str = "",
        category: str = "",
    ) -> dict[str, str | int]:
        """Capture an idea on the backlog — GitHub issue + Project Backlog.

        Infer `category` and `theme` unless the user sets them. Types:

        - Defect: unexpected or wrong current behavior (the kit should already do this).
        - Small change: a change to an existing feature, utility, or tool. Those are all Small changes unless the addition is very large.
        - Refactor: changing code and where things are without changing functionality.
        - Feature: standing up a new module (a new folder). Example: creating the CLI agent. A small change to an existing feature is not a Feature.
        """
        destination = str(self._repo_root(workspace))
        handoff = self._handoff()
        handoff_md = handoff._render_handoff_markdown(
            handoff._collect_state(destination), next_focus=focus
        )
        body = self._backlog_issue_body(handoff_md, focus=focus, context=context)
        return self.capture_backlog(
            focus=focus,
            body=body,
            workspace=workspace,
            theme=theme,
            category=category,
            infer_from=f"{focus}\n{context}",
        )

    def _backlog_issue_body(self, handoff_md: str, focus: str, context: str) -> str:
        parts = [(handoff_md or "").strip()]
        request: list[str] = []
        if focus.strip():
            request.append(f"**Focus:** {focus.strip()}")
        if context.strip():
            request.append(context.strip())
        if request:
            parts.extend(["", "## Request", "", *request])
        return "\n".join(part for part in parts if part is not None).strip() + "\n"

    @agent_tool
    def capture_backlog(
        self,
        focus: str,
        body: str,
        workspace: str = "",
        theme: str = "",
        category: str = "",
        infer_from: str = "",
    ) -> dict[str, str | int]:
        """Create a GitHub issue whose body is the handoff text, Project Backlog."""
        issue_body = self._handoff_issue_body(body)
        return self.create_ticket(
            title=focus.strip() or "backlog",
            body=issue_body,
            workspace=workspace,
            project_status="Backlog",
            theme=theme,
            category=category,
            infer_from=infer_from or f"{focus}\n{body}",
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
        flow: str = "",
    ) -> dict[str, str | int]:
        """Start work from a GitHub issue.

        With ``flow`` set (e.g. ``/start-ticket /small-work 14``): move the issue
        off inbox Project 1 onto that flow's Project first state (creates a Turn).
        Without ``flow``: keep today's inbox behavior — In Progress on Project 1.
        Kit + board only — no GitHub Actions.
        """
        viewed = self.view_ticket(ticket, workspace=workspace)
        if flow.strip():
            self.name = flow.strip()
            self.set_ticket_project_status(
                ticket, "In Progress", workspace=workspace, project=flow.strip()
            )
        else:
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
        return {**viewed, **opened, "flow": flow.strip()}

    @prompt(name="finish-plan")
    @agent_tool
    def finish_plan(
        self,
        workspace: str = "",
        tickets: str = "",
    ) -> dict[str, str | bool]:
        """Operator gate after flow-done: inbox Done, close issues, drop throwaway Project/yaml.

        Flow-done cards stay on the flow board until this runs. Saved Workflows keep
        their Project and ``workflow/flows/{name}.yaml``; throwaway ones are deleted.
        """
        closed: list[str] = []
        for raw in (tickets or "").replace(",", " ").split():
            ref = raw.strip()
            if not ref:
                continue
            self.set_ticket_project_status(ref, "Done", workspace=workspace)
            self.close_ticket(ref, workspace=workspace)
            closed.append(ref)
        deleted_throwaway = False
        if self.throwaway:
            if self.flow_file_path is not None and self.flow_file_path.is_file():
                self.flow_file_path.unlink()
                deleted_throwaway = True
            self.flow_project_number = None
        return {
            "closed": ",".join(closed),
            "throwaway_deleted": deleted_throwaway,
            "workflow": self.name,
        }

    def compose_throwaway(self, name: str, workspace: str = "") -> "Workflow":
        """Compose a one-off Workflow (temp Project + yaml deleted on /finish-plan)."""
        self.name = name.strip()
        self.throwaway = True
        root = Path(workspace.strip() or self._workspace_path or ".")
        path = root / "workflow" / "flows" / f"{self.name}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"name: {self.name}\nthrowaway: true\nstates: {{}}\n",
            encoding="utf-8",
        )
        self.flow_file_path = path
        return self

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
        if session is not None and (
            session.open_turn is not None
            or session.git.is_dirty(untracked=False)
        ):
            session.turn.finish(
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
        theme: str = "",
        category: str = "",
        infer_from: str = "",
    ) -> dict[str, str | int]:
        if project_status not in _PROJECT_STATUSES:
            raise ValueError(f"project_status must be one of {_PROJECT_STATUSES}")
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        self._ensure_project(repo, repo_root)
        work = WorkTicket(repo, self).create(
            title,
            body,
            type=category,
            theme=theme,
            status=project_status,
            infer_from=infer_from or f"{title}\n{body}",
        )
        return work.as_dict(project_status=project_status)

    def set_ticket_project_status(
        self,
        ticket: str,
        status: str,
        workspace: str = "",
        project: str = "",
    ) -> str:
        """Move ticket Status on inbox (default) or on a named flow Project."""
        if status not in _PROJECT_STATUSES and not project.strip():
            raise ValueError(f"status must be one of {_PROJECT_STATUSES}")
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        issue = repo.ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        if project.strip():
            # Flow board: kit writes Status on that Workflow's Project (columns from GitHub).
            self.name = project.strip()
            board = repo.attach_project_named(project.strip()) if hasattr(repo, "attach_project_named") else self._ensure_project(repo, repo_root)
            if board is not None and hasattr(issue, "set_status_on"):
                issue.set_status_on(board, status)
            else:
                issue.set_status(status)
        else:
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
        if session.git.is_dirty(untracked=False):
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
