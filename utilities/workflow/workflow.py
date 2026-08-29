# @toolset-manifest python -m tools manifest workflow.workflow:Workflow
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Workflow — backlog, start, finish linking GitHub Issues, handoff, and WorkSession."""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
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
    @agent_tool
    def backlog(
        self,
        focus: str,
        context: str = "",
        workspace: str = "",
        theme: str = "",
        category: str = "",
    ) -> dict[str, str]:
        """Capture an idea on the backlog — GitHub issue + Project Backlog.

        Runs as a non-blocking sub-agent so the current work is not interrupted.
        Commits the current turn first to capture state, collects the chat
        transcript path and git turn context (branch, commit, recent log), then
        launches a background sub-agent to analyze when and where the issue
        occurred and create the GitHub issue with that enriched handoff.

        Infer `category` and `theme` unless the user sets them. Types:

        - Defect: unexpected or wrong current behavior (the kit should already do this).
        - Small change: a change to an existing feature, utility, or tool. Those are all Small changes unless the addition is very large.
        - Refactor: changing code and where things are without changing functionality.
        - Feature: standing up a new module (a new folder). Example: creating the CLI agent. A small change to an existing feature is not a Feature.
        """
        destination = str(self._repo_root(workspace))

        git_ctx = self._collect_git_context(workspace)
        head_sha = self._commit_if_dirty(workspace, focus)
        git_ctx["head_sha"] = head_sha

        transcript_path = self._find_transcript_path(workspace)

        handoff = self._handoff()
        handoff_md = handoff._render_handoff_markdown(
            handoff._collect_state(destination), next_focus=focus
        )
        base_body = self._backlog_issue_body(handoff_md, focus=focus, context=context)
        turn_md = self._format_turn_context(git_ctx, transcript_path)
        full_body = base_body.rstrip() + "\n\n" + turn_md + "\n"

        meta_path = self._write_backlog_staging(
            workspace=workspace,
            focus=focus,
            body=full_body,
            metadata={
                "focus": focus,
                "workspace": destination,
                "theme": theme,
                "category": category,
                "infer_from": f"{focus}\n{context}",
                "transcript_path": transcript_path,
                "git": git_ctx,
            },
        )

        return self._launch_backlog_agent(workspace, str(meta_path), focus)

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

    def _collect_git_context(self, workspace: str = "") -> dict[str, str]:
        """Collect branch, commit SHA, and recent log for turn attribution."""
        ctx: dict[str, str] = {"branch": "", "head_sha": "", "log": ""}
        try:
            repo = self._repo(workspace)
            ctx["branch"] = repo.current_branch
            ctx["head_sha"] = repo.current_commit
        except Exception:
            pass
        try:
            root = self._repo_root(workspace)
            result = subprocess.run(
                ["git", "log", "-10", "--oneline", "--decorate", "--all"],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            ctx["log"] = result.stdout.strip()
        except Exception:
            pass
        return ctx

    def _find_transcript_path(self, workspace: str = "") -> str:
        """Locate the most recent Cursor agent transcript for this workspace."""
        try:
            root = self._repo_root(workspace)
            raw = str(root.resolve())
            slug = raw.replace(":", "").replace("\\", "-").replace("/", "-").lower()
            transcripts_dir = Path.home() / ".cursor" / "projects" / slug / "agent-transcripts"
            if not transcripts_dir.is_dir():
                return ""
            files = sorted(
                transcripts_dir.rglob("*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            return str(files[0]) if files else ""
        except Exception:
            return ""

    def _commit_if_dirty(self, workspace: str = "", focus: str = "") -> str:
        """Commit staged/tracked changes to close the current turn before staging the backlog."""
        try:
            ws = self._workspace(workspace)
            session = ws.current_work_session
            repo = self._repo(workspace)
            if not repo.is_dirty(untracked=False):
                return repo.current_commit
            subject = (
                f"backlog: {focus.strip()[:60]}" if focus.strip() else "backlog: close turn"
            )
            if session is not None:
                session.turn.finish(
                    prompt=focus,
                    result=subject,
                    context=session.name,
                )
            return repo.current_commit
        except Exception:
            try:
                return self._repo(workspace).current_commit
            except Exception:
                return ""

    def _format_turn_context(self, git_ctx: dict[str, str], transcript_path: str) -> str:
        """Render a markdown Turn Context section from collected git and transcript metadata."""
        lines: list[str] = ["## Turn Context", ""]
        if git_ctx.get("branch"):
            lines.append(f"- **Branch:** `{git_ctx['branch']}`")
        if git_ctx.get("head_sha"):
            sha = git_ctx["head_sha"]
            lines.append(f"- **Commit:** `{sha[:12] if len(sha) >= 12 else sha}`")
        if transcript_path:
            lines.append(f"- **Transcript:** `{transcript_path}`")
        if git_ctx.get("log"):
            lines.extend(["", "### Recent Commits", "", "```", git_ctx["log"], "```"])
        return "\n".join(lines)

    def _write_backlog_staging(
        self,
        workspace: str,
        focus: str,
        body: str,
        metadata: dict,
    ) -> Path:
        """Write the enriched backlog body and metadata to .context/ staging files."""
        root = self._repo_root(workspace)
        staging_dir = root / ".context"
        staging_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        slug = self._kebab(focus)[:40]

        body_path = staging_dir / f"backlog-{slug}-{ts}.md"
        body_path.write_text(body, encoding="utf-8")

        meta: dict = {**metadata, "body_path": str(body_path)}
        meta_path = staging_dir / f"backlog-{slug}-{ts}.json"
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        return meta_path

    def _backlog_agent_task(self, meta_path: str, focus: str) -> str:
        """Build the task prompt for the backlog sub-agent."""
        return (
            f"Backlog task — {focus!r}\n\n"
            f"Metadata file: {meta_path}\n\n"
            "Steps:\n"
            "1. Read the metadata JSON at the path above. It contains: focus, workspace,\n"
            "   theme, category, infer_from, body_path, transcript_path, and git context.\n"
            "2. Read body_path — this is the pre-built handoff body including Turn Context.\n"
            "3. If transcript_path is non-empty and the file exists, read it and scan for\n"
            "   the turn where this issue was first identified. Determine whether the\n"
            "   change occurred in the current turn (commit listed in the Turn Context)\n"
            "   or an earlier one, and note the branch and commit SHA. Update the Turn\n"
            "   Context section in the body with those specifics before calling capture_backlog.\n"
            "4. Call capture_backlog with:\n"
            "   - focus: from metadata\n"
            "   - body: the updated body content (or body_path if unchanged)\n"
            "   - workspace: from metadata\n"
            "   - theme: from metadata\n"
            "   - category: from metadata\n"
            "   - infer_from: from metadata\n"
        )

    def _launch_backlog_agent(
        self,
        workspace: str,
        meta_path: str,
        focus: str,
    ) -> dict[str, str]:
        """Spawn a non-blocking CliAgent sub-agent to analyze context and create the issue."""
        from cli_agent.cli_agent import CliAgent

        ws_root = str(self._repo_root(workspace))
        agent = CliAgent(workspace=ws_root)
        agent.task_prompt = self._backlog_agent_task(meta_path, focus)
        report = agent.launch_sessions(tools=["workflow.workflow:Workflow"])
        return {"launched": "yes", "staging": meta_path, "report": str(report)}

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
