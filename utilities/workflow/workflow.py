# @toolset-manifest python -m tools manifest workflow.workflow:Workflow
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Workflow — backlog, start, finish linking GitHub Issues, handoff, and WorkSession."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml

from git import Ticket, TicketNotFoundError
from git.git import Repo
from handoff.handoff import Handoff
from harness.harness_tool import prompt, skill
from primitives.actions.action import agent_instructions, agentic_toolset
from sub_agent.sub_agent import sub_agent
from tools.tool import agent_tool
from workflow.work_ticket import WorkTicket
from workspace import Workspace
from workspace.git_repo import NullGitRepo
from workspace.workspace import Turn


@dataclass(frozen=True)
class WorkflowConfig:
    project_owner: str
    project_number: int
    default_branch: str = "main"


@agentic_toolset
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
        self._repos: dict[str, Repo] = {}

    def _repo_root(self, workspace: str = "") -> Path:
        start = workspace.strip() or self._workspace_path or "."
        root = Repo.find_root(start)
        if root is None:
            raise ValueError(f"not a git clone: {start!r}")
        return root

    def _repo(self, workspace: str = "") -> Repo:
        if self._repo_override is not None:
            return self._repo_override
        root = str(self._repo_root(workspace))
        cached = self._repos.get(root)
        if cached is not None:
            return cached
        repo = Repo.open(root)
        self._repos[root] = repo
        return repo

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

    def _ticket_from_session_name(self, session_name: str) -> str:
        """Trailing ``-{n}`` on the work-session slug is the GitHub issue number."""
        match = re.search(r"-(\d+)$", (session_name or "").strip())
        return match.group(1) if match else ""

    def _resolve_finish_ticket(self, ticket: str, session_name: str) -> str:
        resolved = (ticket or "").strip() or self._ticket_from_session_name(session_name)
        if not resolved:
            raise ValueError(
                "finish-ticket needs a ticket (pass ticket=) or a session name ending "
                "in -{issue-number} so the project card can move to Done"
            )
        return resolved

    def _workflow_config_path(self, repo_root: Path) -> Path:
        return repo_root / ".context" / "workflow.yaml"

    def _workflow_rules_path(self, repo_root: Path) -> Path:
        return repo_root / ".context" / "workflow-rules.yaml"

    def _load_workflow_rules(self, workspace: str = "") -> list[str]:
        """Read the repo's agentic workflow rules; empty when the file is absent."""
        path = self._workflow_rules_path(self._repo_root(workspace))
        if not path.is_file():
            return []
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rules = payload.get("rules") if isinstance(payload, dict) else payload
        return [str(rule).strip() for rule in (rules or []) if str(rule).strip()]

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
            repo.project.refresh_states()
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

        Commits the current turn to capture state, then returns a ready-to-launch
        sub-agent task. After this tool returns, launch a non-blocking sub-agent
        (via /sub-agent with workflow.workflow:Workflow) using the returned
        ``sub_agent_task`` as the prompt. Do not call capture_backlog inline.

        Infer `category` and `theme` unless the user sets them. Types:

        - Defect: unexpected or wrong current behavior (the kit should already do this).
        - Small change: a change to an existing feature, utility, or tool. Those are all Small changes unless the addition is very large.
        - Refactor: changing code and where things are without changing functionality.
        - Feature: standing up a new module (a new folder). Example: creating the CLI agent. A small change to an existing feature is not a Feature.
        """
        destination = str(self._repo_root(workspace))

        self._commit_if_dirty(workspace, focus)
        transcript_path = self._find_transcript_path(workspace)

        handoff = self._handoff()
        handoff_md = handoff._render_handoff_markdown(
            handoff._collect_state(destination), next_focus=focus
        )
        body = self._backlog_issue_body(handoff_md, focus=focus, context=context)

        return {
            "committed": "yes",
            "tools": "workflow.workflow:Workflow",
            "sub_agent_task": self._backlog_task_prompt(
                focus=focus,
                body=body,
                workspace=destination,
                theme=theme,
                category=category,
                infer_from=f"{focus}\n{context}",
                transcript_path=transcript_path,
            ),
        }

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
                turn = session.open_turn or Turn(root=str(repo.root))
                turn.turn(
                    commit_message=subject,
                    utility="backlog",
                    subject=session.name,
                )
            return repo.current_commit
        except Exception:
            try:
                return self._repo(workspace).current_commit
            except Exception:
                return ""

    def _backlog_task_prompt(
        self,
        focus: str,
        body: str,
        workspace: str,
        theme: str,
        category: str,
        infer_from: str,
        transcript_path: str,
    ) -> str:
        """Build the task prompt for the backlog sub-agent."""
        lines = [f"Backlog task — {focus!r}", ""]
        if transcript_path:
            lines += [
                f"Transcript: {transcript_path}",
                "",
                "Read the transcript and identify which chat turn first noticed this issue.",
                "Determine whether the change that caused it is in the current commit",
                "(shown in the Turn Context below) or an earlier one, and note the branch",
                "and commit SHA. Update the Turn Context section in the body accordingly.",
                "",
            ]
        lines += [
            "Then call capture_backlog with:",
            f"  focus: {focus!r}",
            f"  body: (the body below, updated with transcript findings)",
            f"  workspace: {workspace!r}",
            f"  theme: {theme!r}",
            f"  category: {category!r}",
            f"  infer_from: {infer_from!r}",
            "",
            "--- body ---",
            body.rstrip(),
        ]
        return "\n".join(lines)

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
    @sub_agent
    @agent_tool
    def start(
        self,
        ticket: str,
        instructions: str = "",
        workspace: str = "",
        copy_body: bool = False,
        workflow_state: str = "specification",
    ) -> dict[str, str | int]:
        """Start work from a GitHub issue — In Progress, WorkSession, session branch.

        ``kind: sub_agent`` / ``launch: non_blocking`` — the parent launches a sub-agent
        for this operation and does not wait. Inside that sub-agent, run start (In Progress,
        open WorkSession, session branch) then continue the ticket work.
        """
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
        if session is not None and session.git.is_dirty(untracked=False):
            message = self.turn_commit_message(
                subject=f"start {session.name}",
                ticket=ticket,
                workflow_state=workflow_state,
                workspace=workspace,
            )
            turn = session.open_turn or Turn(root=str(session.git.root))
            turn.turn(commit_message=message, utility="start-ticket")
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
        """Finish the open WorkSession — merge to main, Done on the project board, close issue, close session.

        Always moves the GitHub Project Status to **Done** (not issue-closed alone).
        Pass ``ticket`` or rely on the session slug's trailing ``-{issue}``.

        Before calling: in the session worktree run ``git status``. Delete only temps
        you know are ephemeral from this session (deploy output, agent BDD run logs,
        scratch request files). Use session context — do not delete durable artifacts.
        Then call finish so merge and worktree removal can proceed on a clean tree.
        """
        session_name = self.require_open_session(workspace=workspace)
        resolved_ticket = self._resolve_finish_ticket(ticket, session_name)
        ws = self._workspace(workspace)
        session = ws.current_work_session
        if session is not None and session.git.is_dirty(untracked=False):
            Turn(root=str(session.git.root)).turn(
                message=outcome or "finish",
                utility="finish-ticket",
                subject=session_name,
            )
            session.open_turn = None
        sha = self.merge_session_to_main(
            workspace=workspace, ticket=resolved_ticket, reviewed_by=reviewed_by
        )
        # Always move the Kanban Status to Done, then close the GitHub issue.
        self.set_ticket_project_status(resolved_ticket, "Done", workspace=workspace)
        self.close_ticket(resolved_ticket, workspace=workspace)
        if session is not None:
            session.close_session(outcome=outcome or "finished")
        return {
            "commit": sha,
            "session_name": session_name,
            "ticket": resolved_ticket,
            "project_status": "Done",
        }

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

    @prompt(name="ticket-rules")
    @agent_tool
    def read_ticket_rules(self, workspace: str = "") -> dict[str, object]:
        """Read the repo's workflow rules that govern every ticket action."""
        return {"rules": self._load_workflow_rules(workspace)}

    @prompt(name="update-ticket-labels")
    @agent_tool
    def update_ticket_labels(
        self,
        ticket: str,
        add: str = "",
        remove: str = "",
        workspace: str = "",
    ) -> dict[str, str | int]:
        """Update ticket labels: add and/or remove comma-separated labels."""
        issue = self._require_ticket(self._repo(workspace), ticket)
        for label in (part.strip() for part in remove.split(",")):
            issue.remove_label(label)
        for label in (part.strip() for part in add.split(",")):
            issue.add_label(label)
        return {
            "number": issue.number,
            "title": issue.title,
            "labels": ", ".join(sorted(set(issue.labels))),
        }

    @skill(name="tickets")
    @prompt(name="tickets")
    @agent_instructions
    def manage_tickets(self, request: str, workspace: str = "") -> str:
        """Manage project tickets from {{request}}.

        Start by calling read_ticket_rules and follow every rule it returns; the repo's
        rules override defaults. Display each available ticket tool name and purpose
        before acting. Call list_project_statuses when you need the board columns.
        Then review ticket statuses so board state and left-to-right column order are
        known. Then call only the tool needed to move a ticket, add a
        child ticket, merge a completed child into its parent, update a ticket, update
        labels, align children to parent, or report board status. Never infer a ticket
        number when the request is ambiguous.
        """
        self.read_ticket_rules(workspace=workspace)
        self.review_ticket_statuses(workspace=workspace)
        self.move_ticket(ticket="", destination="", workspace=workspace)
        self.add_child_ticket(parent="", title="", workspace=workspace)
        self.merge_child_into_parent(child="", summary="", workspace=workspace)
        self.update_ticket(ticket="", workspace=workspace)
        self.update_ticket_labels(ticket="", workspace=workspace)
        self.align_child_tickets_to_parent(parent="", workspace=workspace)
        return "Ticket request completed."

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

    @agent_tool
    def list_project_statuses(self, workspace: str = "") -> dict[str, object]:
        """List GitHub Project Status columns left-to-right for move_ticket destinations."""
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        project = self._ensure_project(repo, repo_root)
        statuses = project.status_option_names()
        return {
            "project": f"{project.owner}#{project.number}",
            "statuses": statuses,
            "hint": "Pass any status name to move_ticket(destination=...), or use next/previous.",
        }

    @prompt(name="move-ticket")
    @agent_tool
    def move_ticket(
        self,
        ticket: str,
        destination: str,
        workspace: str = "",
        align_children: bool = True,
    ) -> dict[str, object]:
        """Move a ticket to any Project Status column, or to next/previous. Follow the repo workflow rules (read_ticket_rules)."""
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        project = self._ensure_project(repo, repo_root)
        issue = self._require_ticket(repo, ticket)
        status = self._destination_status(project, issue.number, destination)
        issue.set_status(status)
        result: dict[str, object] = {
            **self.view_ticket(ticket, workspace),
            "project_status": status,
        }
        if align_children:
            aligned = self._align_child_tickets_for_parent(
                project, issue, workspace, self._board_status_map(project)
            )
            if aligned:
                result["aligned_children"] = aligned
        return result

    def _destination_status(self, project, ticket_number: int, destination: str) -> str:
        requested = destination.strip()
        if not requested:
            raise ValueError("destination requires a board state, next, or previous")
        direction = requested.lower()
        if direction not in ("next", "previous", "prev"):
            return project.state_named(requested).name
        statuses = project.status_option_names()
        current = self._ticket_status(project, ticket_number)
        if not current:
            raise ValueError(f"ticket {ticket_number} is not on the project board")
        index = statuses.index(current)
        offset = 1 if direction == "next" else -1
        target = max(0, min(index + offset, len(statuses) - 1))
        return statuses[target]

    def _ticket_status(self, project, ticket_number: int) -> str:
        for row in project.ticket_rows():
            if row["number"] == ticket_number:
                return str(row["status"])
        return ""

    @prompt(name="add-child-ticket")
    @agent_tool
    def add_child_ticket(
        self,
        parent: str,
        title: str,
        body: str = "",
        workspace: str = "",
        project_status: str = "Backlog",
        theme: str = "",
        category: str = "",
    ) -> dict[str, str | int]:
        """Create a project ticket and attach it as a direct child of a parent issue. Follow the repo workflow rules (read_ticket_rules)."""
        repo = self._repo(workspace)
        parent_issue = self._require_ticket(repo, parent)
        created = self.create_ticket(
            title=title,
            body=body,
            workspace=workspace,
            project_status=project_status,
            theme=theme,
            category=category,
        )
        child = self._require_ticket(repo, str(created["number"]))
        parent_issue.add_child(child)
        project = self._ensure_project(repo, self._repo_root(workspace))
        ancestors = self._ticket_ancestors(repo, parent_issue)
        ultimate_parent = ancestors[-1]
        for issue in (child, *ancestors):
            project.set_text_field(issue.number, "Ultimate Parent", ultimate_parent.title)
        return {
            **created,
            "parent": parent_issue.number,
            "ultimate_parent": ultimate_parent.title,
        }

    def _ticket_ancestors(self, repo: Repo, issue: Ticket) -> list[Ticket]:
        ancestors = [issue]
        seen = {issue.number}
        while ancestors[-1].parent_number is not None:
            parent = self._require_ticket(repo, str(ancestors[-1].parent_number))
            if parent.number in seen:
                raise ValueError(f"cycle in ticket parents at {parent.number}")
            ancestors.append(parent)
            seen.add(parent.number)
        return ancestors

    @prompt(name="merge-child-into-parent")
    @agent_tool
    def merge_child_into_parent(
        self,
        child: str,
        summary: str,
        workspace: str = "",
    ) -> dict[str, str | int]:
        """Roll a completed child result into its parent.

        Close and archive the child while preserving the sub-issue relationship.
        """
        repo = self._repo(workspace)
        child_issue = self._require_ticket(repo, child)
        if child_issue.parent_number is None:
            raise ValueError(f"ticket {child_issue.number} has no parent")
        parent = self._require_ticket(repo, str(child_issue.parent_number))
        result = summary.strip()
        if not result:
            raise ValueError("summary is required")
        child_link = child_issue.url or f"#{child_issue.number}"
        heading = f"## Completed child: [{child_issue.title}]({child_link})"
        merged_section = f"{heading}\n\n{result}"
        if heading not in parent.body:
            parent.update(body=f"{parent.body.rstrip()}\n\n{merged_section}\n")
        child_issue.comment(
            f"Result merged into parent #{parent.number}.\n\n{result}"
        )
        project = self._ensure_project(repo, self._repo_root(workspace))
        child_issue.set_status(project.state_named("Done").name)
        child_issue.close()
        project.archive_ticket(child_issue.number)
        return {
            "child": child_issue.number,
            "parent": parent.number,
            "project_status": "Done",
            "archived": "yes",
        }

    def _require_ticket(self, repo: Repo, ticket: str) -> Ticket:
        issue = repo.ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        return issue

    @prompt(name="update-ticket")
    @agent_tool
    def update_ticket(
        self,
        ticket: str,
        title: str | None = None,
        body: str | None = None,
        workspace: str = "",
    ) -> dict[str, str | int]:
        """Update a ticket title and/or body; omitted values remain unchanged. Follow the repo workflow rules (read_ticket_rules)."""
        issue = self._require_ticket(self._repo(workspace), ticket)
        normalized_title = title.strip() if title is not None else None
        issue.update(title=normalized_title, body=body)
        return self.view_ticket(ticket, workspace)

    @prompt(name="review-ticket-statuses")
    @agent_tool
    def review_ticket_statuses(
        self,
        workspace: str = "",
        status: str = "",
    ) -> dict[str, object]:
        """List project tickets by board columns from left to right, optionally filtered. Follow the repo workflow rules (read_ticket_rules)."""
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        project = self._ensure_project(repo, repo_root)
        statuses = project.status_option_names()
        if status.strip():
            statuses = [project.state_named(status.strip()).name]
        rows = project.ticket_rows()
        columns = [self._ticket_column(name, rows) for name in statuses]
        return {
            "columns": columns,
            "total": sum(len(column["tickets"]) for column in columns),
        }

    @prompt(name="align-child-tickets-to-parent")
    @agent_tool
    def align_child_tickets_to_parent(
        self,
        parent: str = "",
        workspace: str = "",
    ) -> dict[str, object]:
        """Align child tickets so no child is in a board column prior to its parent. Follow the repo workflow rules (read_ticket_rules)."""
        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        project = self._ensure_project(repo, repo_root)
        aligned: list[dict[str, object]] = []

        if parent.strip():
            parent_issue = self._require_ticket(repo, parent)
            aligned.extend(
                self._align_child_tickets_for_parent(
                    project, parent_issue, workspace, self._board_status_map(project)
                )
            )
        else:
            statuses_by_number = self._board_status_map(project)
            for number in statuses_by_number:
                parent_issue = repo.ticket(str(number))
                if parent_issue and parent_issue.sub_issue_numbers:
                    aligned.extend(
                        self._align_child_tickets_for_parent(
                            project, parent_issue, workspace, statuses_by_number
                        )
                    )

        return {
            "parent": parent if parent.strip() else "all",
            "aligned": aligned,
            "total_aligned": len(aligned),
        }

    def _board_status_map(self, project) -> dict[int, str]:
        """Read the board once and map ticket number to its column."""
        return {
            int(row["number"]): str(row["status"])
            for row in project.ticket_rows()
        }

    def _align_child_tickets_for_parent(
        self,
        project,
        parent_issue: Ticket,
        workspace: str,
        statuses_by_number: dict[int, str],
    ) -> list[dict[str, object]]:
        aligned: list[dict[str, object]] = []
        parent_status = statuses_by_number.get(parent_issue.number, "")
        if not parent_status:
            return aligned
        statuses = project.status_option_names()
        if parent_status not in statuses:
            return aligned
        parent_idx = statuses.index(parent_status)

        repo = self._repo(workspace)
        for child_num in list(parent_issue.sub_issue_numbers):
            child_status = statuses_by_number.get(child_num, "")
            if not child_status or child_status not in statuses:
                continue
            child_idx = statuses.index(child_status)
            if child_idx < parent_idx:
                child_issue = repo.ticket(str(child_num))
                if child_issue:
                    child_issue.set_status(parent_status)
                    statuses_by_number[child_num] = parent_status
                    aligned.append(
                        {
                            "child": child_num,
                            "from_status": child_status,
                            "to_status": parent_status,
                        }
                    )
                    if child_issue.sub_issue_numbers:
                        aligned.extend(
                            self._align_child_tickets_for_parent(
                                project, child_issue, workspace, statuses_by_number
                            )
                        )
        return aligned

    def _ticket_column(
        self, status: str, rows: list[dict[str, str | int]]
    ) -> dict[str, object]:
        tickets = [row for row in rows if row["status"] == status]
        tickets.sort(key=lambda row: int(row["number"]))
        return {"status": status, "tickets": tickets}

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
        from workflow.work_ticket import format_session_ticket_context

        repo_root = self._repo_root(workspace)
        repo = self._repo(workspace)
        issue = repo.ticket(ticket)
        if issue is None:
            raise TicketNotFoundError(f"GitHub issue not found: {ticket}")
        session_folder = repo_root / ".sessions" / session_name
        session_folder.mkdir(parents=True, exist_ok=True)
        target = session_folder / filename
        body, _ = format_session_ticket_context(repo, issue.number)
        target.write_text(body or issue.body, encoding="utf-8")
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
