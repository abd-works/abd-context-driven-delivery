"""WorkTicket + Workflow — ticket create/start/finish for #55 redesign (InMemory gh)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agents.agent import (
    Agent,
    AgentParticipant,
    AgentSession,
    AgentTask,
    Issue,
    Repo,
    SubAgent,
    Workspace,
)


@dataclass(frozen=True)
class WorkflowConfig:
    """Workflow project defaults — properties only."""

    project_owner: str = "local"
    project_number: int = 1
    default_branch: str = "main"


@dataclass(frozen=True)
class StartTicketResult:
    """Outcome of Workflow.start — session, worktree, and issue-body path."""

    number: int
    title: str
    body: str
    session_name: str
    branch: str
    worktree: str
    context_root: str
    issue_body_path: str
    agent_type: str


@dataclass(frozen=True)
class _SessionOpenPlan:
    """Pure plan for opening a ticket session — no I/O."""

    name: str
    folder: Path
    context_root: Path
    goal: str
    sibling_path: Path


@dataclass(frozen=True)
class _SessionOpenRequest:
    """Inputs absorbed for session open planning."""

    session_name: str
    repo_root: Path
    context_root: Path
    goal: str
    issue_number: int


class _TicketNaming:
    """Kebab session names and sibling worktree path calculation."""

    @staticmethod
    def kebab(text: str) -> str:
        cleaned = "".join(
            character.lower() if character.isalnum() else "-"
            for character in text.strip()
        )
        while "--" in cleaned:
            cleaned = cleaned.replace("--", "-")
        return cleaned.strip("-") or "idea"

    @classmethod
    def session_name(cls, title: str, number: int) -> str:
        slug = cls.kebab(title)
        if slug:
            return f"{slug}-{number}"
        return f"issue-{number}"

    @staticmethod
    def abbreviate_repo_name(folder: str) -> str:
        tokens = [part for part in re.split(r"[-_]+", folder or "") if part]
        if not tokens:
            return folder
        if len(tokens) == 1:
            return tokens[0]
        return tokens[0] + "-" + "".join(token[0] for token in tokens[1:])

    @classmethod
    def sibling_path(cls, primary: Path, issue_number: int) -> Path:
        abbrev = cls.abbreviate_repo_name(primary.name)
        return primary.parent / f"{abbrev}-{issue_number}"


class _ProjectStatusName:
    """Pure project-status name from issue + status map."""

    @staticmethod
    def resolve(issue: "Issue | None", status_by_number: dict[int, str]) -> str:
        if issue is None:
            return ""
        if issue.state is not None:
            return issue.state.name
        number = issue.number
        if number in status_by_number:
            return status_by_number[number]
        return ""


class _SessionOpenPlanner:
    """Build an open plan from ticket + workflow paths — no I/O."""

    def __init__(self, path_type: type[Path] = Path) -> None:
        self._path_type = path_type

    def plan(self, request: _SessionOpenRequest) -> _SessionOpenPlan:
        root = self._path_type(request.repo_root)
        name = request.session_name
        return _SessionOpenPlan(
            name=name,
            folder=root / ".agent_sessions" / name,
            context_root=self._path_type(request.context_root),
            goal=request.goal,
            sibling_path=_TicketNaming.sibling_path(root, request.issue_number),
        )


class _IssueBodyFile:
    """Issue body path calc + text write (I/O isolated)."""

    def __init__(self, path_type: type[Path] = Path) -> None:
        self._path_type = path_type

    def target_under(self, context_root: Path) -> Path:
        return self._path_type(context_root) / "issue-body.md"

    def write(self, context_root: Path, body: str) -> Path:
        target = self.target_under(context_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return target


_DEFAULT_SESSION_PLANNER = _SessionOpenPlanner()
_DEFAULT_ISSUE_BODY_FILE = _IssueBodyFile()


class _TicketLabels:
    """Type/theme/status/as_dict helpers for a WorkTicket."""

    def __init__(self, ticket: WorkTicket) -> None:
        self._ticket = ticket

    def set_type(self, name: str) -> WorkTicket:
        text = (name or "").strip()
        self._ticket._type = text
        issue = self._ticket._issue
        if text and issue is not None:
            issue.set_type(text)
        ticket = self._ticket
        return ticket

    def set_theme(self, theme: str) -> WorkTicket:
        slug = (theme or "").strip()
        if slug.lower().startswith("theme:"):
            slug = slug.split(":", 1)[1].strip()
        self._ticket._theme = slug
        issue = self._ticket._issue
        if slug and issue is not None:
            issue.add_theme(slug)
        ticket = self._ticket
        return ticket

    def set_status(self, state: str) -> WorkTicket:
        issue = self._ticket._issue
        if issue is not None:
            issue.set_status(state)
        ticket = self._ticket
        return ticket

    def as_dict(self) -> dict[str, "str | int"]:
        ticket = self._ticket
        issue = ticket._issue
        payload: dict[str, "str | int"] = {
            "number": 0 if issue is None else issue.number,
            "title": "" if issue is None else issue.title,
            "body": "" if issue is None else issue.body,
            "url": "" if issue is None else issue.url,
            "project_status": _ProjectStatusName.resolve(
                issue, ticket._repo._issue_shelf.status_map()
            ),
        }
        if ticket._type:
            payload["type"] = ticket._type
        elif issue is not None and issue.issue_type:
            payload["type"] = issue.issue_type
        if ticket._theme:
            payload["theme"] = ticket._theme
        return payload


class WorkTicket:
    """Workflow-facing issue with session open and start lifecycle."""

    def __init__(
        self,
        repo: Repo,
        workflow: "Workflow | None" = None,
        issue: "Issue | None" = None,
        *,
        session_planner: "_SessionOpenPlanner | None" = None,
        path_type: type[Path] = Path,
    ) -> None:
        self._bind_core(repo, workflow, issue)
        self._bind_collaborators(session_planner)

    def _bind_core(
        self,
        repo: Repo,
        workflow: "Workflow | None",
        issue: "Issue | None",
    ) -> None:
        self._repo = repo
        self._workflow = workflow
        self._issue = issue
        self._type = issue.issue_type if issue is not None else ""
        self._theme = ""
        self._session: "AgentSession | None" = None

    def _bind_collaborators(
        self, session_planner: "_SessionOpenPlanner | None"
    ) -> None:
        self._planner = (
            session_planner
            if session_planner is not None
            else _DEFAULT_SESSION_PLANNER
        )
        self._labels = _TicketLabels(self)

    @classmethod
    def from_ref(
        cls,
        repo: Repo,
        ref: "str | int",
        workflow: "Workflow | None" = None,
    ) -> WorkTicket:
        issue = repo._issue_shelf.lookup(ref)
        ticket = cls(repo, workflow, issue)
        if workflow is not None:
            workflow.ticket = ticket
        return ticket

    @property
    def issue(self) -> "Issue | None":
        return self._issue

    @property
    def session_name(self) -> str:
        return _TicketNaming.session_name(self._issue_title(), self._issue_number())

    def create(self, title: str, body: str, *, type: str = "", theme: str = "") -> WorkTicket:
        self._ensure_project()
        issue = self._repo._issue_shelf.create(title, body)
        issue.set_status("Backlog")
        self._issue = issue
        if type.strip():
            self._labels.set_type(type)
        if theme.strip():
            self._labels.set_theme(theme)
        return self

    def open_session(self, *, instructions: str = "") -> AgentSession:
        workflow = self._require_workflow()
        plan = self._build_open_plan(workflow, instructions=instructions)
        return self._apply_open_plan(workflow, plan)

    def start(self, *, instructions: str = "") -> AgentSession:
        issue = self._require_issue()
        self._ensure_project()
        issue.set_status("In Progress")
        return self.open_session(instructions=instructions)

    def finish(self) -> WorkTicket:
        issue = self._require_issue()
        self._ensure_project()
        self._close_issue_done(issue)
        return self

    def as_dict(self) -> dict[str, "str | int"]:
        return self._labels.as_dict()

    def _bind_workflow(self, workflow: Workflow) -> None:
        self._workflow = workflow

    def _issue_title(self) -> str:
        return "" if self._issue is None else self._issue.title

    def _issue_number(self) -> int:
        return 0 if self._issue is None else self._issue.number

    def _issue_body(self) -> str:
        return "" if self._issue is None else self._issue.body

    def _goal_from_instructions(self, instructions: str) -> str:
        text = instructions.strip()
        if text:
            return text
        return self._issue_title()

    def _build_open_plan(
        self, workflow: Workflow, *, instructions: str
    ) -> _SessionOpenPlan:
        request = _SessionOpenRequest(
            session_name=self.session_name,
            repo_root=self._repo.root,
            context_root=workflow.resolve_context_root(),
            goal=self._goal_from_instructions(instructions),
            issue_number=self._issue_number(),
        )
        return self._planner.plan(request)

    def _apply_open_plan(
        self, workflow: Workflow, plan: _SessionOpenPlan
    ) -> AgentSession:
        session = self._mint_session(plan)
        session.open()
        self._attach_sibling_worktree(session, plan.sibling_path)
        self._remember_session(workflow, session)
        return session

    def _mint_session(self, plan: _SessionOpenPlan) -> AgentSession:
        return AgentSession(
            name=plan.name,
            folder=plan.folder,
            context_root=plan.context_root,
            goal=plan.goal,
            repo=self._repo,
        )

    def _attach_sibling_worktree(
        self, session: AgentSession, sibling_path: Path
    ) -> None:
        session.branch.worktree.create_sibling(sibling_path)

    def _remember_session(
        self, workflow: Workflow, session: AgentSession
    ) -> None:
        self._session = session
        workflow.session = session

    @staticmethod
    def _close_issue_done(issue: Issue) -> None:
        issue.set_status("Done")
        issue.close()

    def _ensure_project(self) -> None:
        shelf = self._repo._issue_shelf
        if shelf.project is None:
            raise RuntimeError("attach_project before WorkTicket operations")

    def _require_workflow(self) -> Workflow:
        workflow = self._workflow
        if workflow is None:
            raise RuntimeError("WorkTicket.openSession requires a Workflow")
        return workflow

    def _require_issue(self) -> Issue:
        issue = self._issue
        if issue is None:
            raise RuntimeError("WorkTicket requires an issue")
        return issue


@dataclass(frozen=True)
class _WorkflowCore:
    """Constructor bundle for Workflow identity and agent defaults."""

    workspace: Workspace
    repo: Repo
    config: WorkflowConfig
    agent: "Agent | None"
    agent_type: str
    path_type: type[Path]


class Workflow:
    """Ticket lifecycle — open session, run, finish issue + session."""

    def __init__(
        self,
        workspace: Workspace,
        repo: Repo,
        config: WorkflowConfig,
        agent: "Agent | None" = None,
        *,
        agent_type: str = "SubAgent",
        issue_body_file: "_IssueBodyFile | None" = None,
        path_type: type[Path] = Path,
    ) -> None:
        self._bind_core(
            _WorkflowCore(workspace, repo, config, agent, agent_type, path_type)
        )
        self._finish_init(issue_body_file)

    def _finish_init(
        self, issue_body_file: "_IssueBodyFile | None"
    ) -> None:
        self._bind_issue_body(issue_body_file)
        self.ticket: "WorkTicket | None" = None
        self.session: "AgentSession | None" = None

    def _bind_core(self, core: _WorkflowCore) -> None:
        self._workspace = core.workspace
        self._repo = core.repo
        self._config = core.config
        self._agent = core.agent
        self._agent_type = core.agent_type
        self._path_type = core.path_type

    def _bind_issue_body(
        self, issue_body_file: "_IssueBodyFile | None"
    ) -> None:
        self._issue_body_file = (
            issue_body_file
            if issue_body_file is not None
            else _DEFAULT_ISSUE_BODY_FILE
        )

    @property
    def workspace(self) -> Workspace:
        return self._workspace

    @property
    def repo(self) -> Repo:
        return self._repo

    @property
    def config(self) -> WorkflowConfig:
        return self._config

    @property
    def agent(self) -> "Agent | None":
        return self._agent

    @agent.setter
    def agent(self, bound_agent: "Agent | None") -> None:
        self._agent = bound_agent

    def create_ticket(self, title: str, body: str, **fields: Any) -> WorkTicket:
        work = WorkTicket(self._repo, self).create(title, body, **fields)
        self.ticket = work
        return work

    def start(
        self,
        ticket: "str | int | WorkTicket",
        *,
        instructions: str = "",
        agent_type: str = "",
    ) -> StartTicketResult:
        work = self._ticket_from(ticket)
        work.start(instructions=instructions)
        session = self._require_started_session(work)
        agent = self._bind_agent(session, self._resolved_agent_type(agent_type))
        self._enqueue_and_run(agent, work, instructions=instructions)
        body_path = self._persist_issue_body(session, work)
        return self._start_result(work, session, agent, body_path)

    def finish(
        self,
        ticket: "str | int | WorkTicket | None" = None,
        *,
        outcome: str = "",
    ) -> WorkTicket:
        """Finish ticket — session finish, issue Done/close, session close."""
        work = self._ticket_for_finish(ticket)
        session = self._require_open_session()
        session.finish(outcome)
        work.finish()
        session.close()
        return work

    def resolve_context_root(self) -> Path:
        override = self._workspace.lookup_path("agent", "contextRoot")
        if override is not None:
            return self._path_type(override)
        return self._path_type(self._repo.root)

    def _ticket_for_finish(
        self, ticket: "str | int | WorkTicket | None"
    ) -> WorkTicket:
        if ticket is None:
            return self._require_ticket()
        return self._ticket_from(ticket)

    def _require_ticket(self) -> WorkTicket:
        work = self.ticket
        if work is None:
            raise RuntimeError("Workflow.finish requires a ticket")
        return work

    def _require_open_session(self) -> AgentSession:
        session = self.session
        if session is None:
            raise RuntimeError("Workflow.finish requires an open AgentSession")
        return session

    def _resolved_agent_type(self, agent_type: str) -> str:
        if agent_type:
            return agent_type
        default_type = self._agent_type
        return default_type

    def _persist_issue_body(
        self, session: AgentSession, work: WorkTicket
    ) -> Path:
        return self._issue_body_file.write(
            session.context_root, self._issue_body_text(work)
        )

    def _issue_body_text(self, work: WorkTicket) -> str:
        issue = work.issue
        if issue is None:
            return ""
        return issue.body

    def _ticket_from(self, ticket: "str | int | WorkTicket") -> WorkTicket:
        if isinstance(ticket, WorkTicket):
            ticket._bind_workflow(self)
            self.ticket = ticket
            return ticket
        work = WorkTicket.from_ref(self._repo, ticket, self)
        self.ticket = work
        return work

    def _require_started_session(self, work: WorkTicket) -> AgentSession:
        session = work._session
        if session is None:
            raise RuntimeError("WorkTicket.start did not open a session")
        return session

    def _enqueue_and_run(
        self, agent: Agent, work: WorkTicket, *, instructions: str
    ) -> None:
        agent.add_tasks([self._task_for(work, instructions=instructions)])
        agent.run_backlog()

    def _bind_agent(self, session: AgentSession, agent_type: str) -> Agent:
        existing = self._agent
        if existing is not None:
            existing.session = session
            session.agent = existing
            return existing
        agent = self._new_agent(session, agent_type)
        self._agent = agent
        session.agent = agent
        return agent

    def _new_agent(self, session: AgentSession, agent_type: str) -> Agent:
        kind = (agent_type or "SubAgent").strip()
        if kind.lower() == "cliagent":
            from agents.agent import CliAgent

            return CliAgent(session=session)
        return SubAgent(session=session)

    def _task_for(self, work: WorkTicket, *, instructions: str) -> AgentTask:
        prompt = self._doer_prompt(work, instructions=instructions)
        return AgentTask(
            prompt=prompt,
            doer=AgentParticipant(type="doer", prompt=prompt),
            tickets=[work],
        )

    def _doer_prompt(self, work: WorkTicket, *, instructions: str) -> str:
        issue = work.issue
        number = 0 if issue is None else issue.number
        title = "" if issue is None else issue.title
        body = "" if issue is None else issue.body
        lines = [
            f"# Ticket #{number}: {title}",
            "",
            body.strip(),
        ]
        if instructions.strip():
            lines.extend(["", "## Start instructions", instructions.strip()])
        return "\n".join(lines).strip() + "\n"

    def _start_result(
        self,
        work: WorkTicket,
        session: AgentSession,
        agent: Agent,
        body_path: Path,
    ) -> StartTicketResult:
        return StartTicketResult(
            number=self._result_number(work),
            title=self._result_title(work),
            body=self._result_body(work),
            session_name=session.name,
            branch=self._result_branch(session),
            worktree=self._result_worktree(session),
            context_root=str(session.context_root),
            issue_body_path=str(body_path),
            agent_type=type(agent).__name__,
        )

    def _result_number(self, work: WorkTicket) -> int:
        issue = work.issue
        if issue is None:
            return 0
        return issue.number

    def _result_title(self, work: WorkTicket) -> str:
        issue = work.issue
        if issue is None:
            return ""
        return issue.title

    def _result_body(self, work: WorkTicket) -> str:
        return self._issue_body_text(work)

    def _result_branch(self, session: AgentSession) -> str:
        if session.branch is None:
            return ""
        return session.branch.name

    def _result_worktree(self, session: AgentSession) -> str:
        if session.worktree is None:
            return ""
        return str(session.worktree.path)
