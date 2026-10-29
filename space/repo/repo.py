"""Local repository + GitHub domain model — branches, commits, project tickets."""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from harness.installation.files import command, skill
from harness.mcp.mcp_server import mcp
from space.repo.latest_release import LatestRelease
from space.work_state import WorkState

logger = logging.getLogger(__name__)


class RepoConnectError(RuntimeError):
    """Raised when the clone cannot be used as a repository."""


_COMMAND_TIMEOUT_SECONDS = 10
# Push, fetch, and pull wait on the network; local git commands should never need this long.
_NETWORK_COMMAND_TIMEOUT_SECONDS = 180
_NETWORK_COMMANDS = frozenset({"push", "fetch", "pull"})


class GhConnectError(RuntimeError):
    """Raised when gh cannot be used."""


class BranchNameRequiredError(ValueError):
    """Raised when a branch command has no name and none is saved in ``.sessions/session.json``."""

    def __init__(self) -> None:
        super().__init__(
            "branch name is required: pass name, or switch to a branch first so "
            "it is saved in .sessions/session.json"
        )


class DefaultBranchError(ValueError):
    """Raised when a branch or worktree command is aimed at the default branch."""

    def __init__(self, operation: str, default: str) -> None:
        super().__init__(f"cannot {operation} the default branch {default!r}")


class BranchInWorktreeError(RuntimeError):
    """Raised when the branch to close is still checked out in a linked worktree."""

    def __init__(self, branch: str, path: Path) -> None:
        super().__init__(
            f"branch {branch!r} is checked out in the worktree at {path}; "
            "close that worktree first"
        )


class NoOpenWorktreeError(RuntimeError):
    """Raised when close-worktree runs with no worktree saved in ``.sessions/session.json``."""

    def __init__(self) -> None:
        super().__init__("no open worktree: .sessions/session.json has no worktree")


class DirtyBranchSwitchError(RuntimeError):
    """Raised when checkout would move a dirty tree onto another branch."""

    def __init__(self, current: str, wanted: str) -> None:
        self.current = current
        self.wanted = wanted
        super().__init__(
            f"Working tree has uncommitted changes on {current!r}; "
            f"not switching to {wanted!r}. Ask whether to bring this work onto "
            f"the session branch, or create a continuation branch "
            f"(e.g. {wanted}-2)."
        )


class TicketNotFoundError(LookupError):
    """Raised when a GitHub issue reference does not resolve."""


DEFAULT_PROJECT_STATES: tuple[str, ...] = ("Backlog", "In Progress", "Done")
# Workflow names first; GitHub Projects often uses Todo instead of Backlog.
GITHUB_STATUS_ALIASES: dict[str, tuple[str, ...]] = {
    "Backlog": ("Todo",),
    "Todo": ("Backlog",),
    "In Progress": ("In progress",),
    "In progress": ("In Progress",),
}
GH_PROJECT_SCOPES_HINT = (
    "Run: gh auth refresh -h github.com -s read:project,project"
)
_ISSUE_NUMBER = re.compile(r"^\d+$")


def theme_slug(theme: str) -> str:
    """Normalized theme slug shared by issue labels and project Theme field."""
    label = issue_theme_label(theme)
    if not label.startswith("theme:"):
        return ""
    return label.split(":", 1)[1]


def issue_theme_label(theme: str) -> str:
    """GitHub issue label for a theme (`theme:<slug>`)."""
    text = (theme or "").strip()
    if text.lower().startswith("theme:"):
        text = text.split(":", 1)[1].strip()
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in text)
    while "--" in slug:
        slug = slug.replace("--", "-")
    slug = slug.strip("-")
    return f"theme:{slug}" if slug else ""


@dataclass
class Commit:
    sha: str
    message: str
    data: dict[str, str] = field(default_factory=dict)

    @classmethod
    def format(cls, subject: str, trailers: dict[str, str] | None = None) -> str:
        lines = [subject.strip()]
        for key, value in (trailers or {}).items():
            text = (value or "").strip()
            if text:
                lines.append(f"{key}: {text}")
        return "\n".join(lines)

    @classmethod
    def from_message(cls, sha: str, message: str) -> Commit:
        commit = cls(sha=sha, message=message)
        commit.data = commit.trailers()
        return commit

    @property
    def subject(self) -> str:
        lines = (self.message or "").splitlines()
        return lines[0].strip() if lines else ""

    def trailers(self) -> dict[str, str]:
        lines = (self.message or "").splitlines()
        if not lines:
            return {}
        data: dict[str, str] = {}
        for line in lines[1:]:
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            data[key.strip()] = value.strip()
        return data

    @classmethod
    def note_text(cls, fields: dict[str, str]) -> str:
        return "\n".join(f"{key}: {value}" for key, value in fields.items())

    def note_payload(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for line in (self.message or "").splitlines():
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            out[key.strip()] = value
        return out


@dataclass
class TicketState:
    name: str

    @classmethod
    def backlog(cls) -> TicketState:
        return cls(DEFAULT_PROJECT_STATES[0])

    @classmethod
    def in_progress(cls) -> TicketState:
        return cls(DEFAULT_PROJECT_STATES[1])

    @classmethod
    def done(cls) -> TicketState:
        return cls(DEFAULT_PROJECT_STATES[2])


@dataclass
class Ticket:
    number: int
    title: str
    body: str
    url: str = ""
    state: TicketState | None = None
    issue_type: str = ""
    labels: list[str] = field(default_factory=list)
    data: dict[str, str] = field(default_factory=dict)
    parent_number: int | None = None
    sub_issue_numbers: list[int] = field(default_factory=list)
    _repo: Repo | None = field(default=None, repr=False, compare=False)

    def bind_repo(self, repo: Repo) -> Ticket:
        self._repo = repo
        return self

    def _require_repo(self, operation: str) -> Repo:
        if self._repo is None:
            raise RuntimeError(f"Ticket.{operation} requires a repo")
        return self._repo

    @property
    def closed(self) -> bool:
        return self.data.get("closed") == "true"

    def close(self) -> None:
        repo = self._require_repo("close")
        if repo.in_memory:
            if not repo.has_ticket(self.number):
                raise TicketNotFoundError(f"GitHub issue not found: {self.number}")
            repo.mark_closed(self.number)
            self.data["closed"] = "true"
            return
        repo.run_gh("issue", "close", str(self.number))
        self.data["closed"] = "true"

    def update(self, *, title: str | None = None, body: str | None = None) -> Ticket:
        """Update supplied issue fields while leaving omitted fields unchanged."""
        repo = self._require_repo("update")
        arguments = ["issue", "edit", str(self.number)]
        if title is not None:
            arguments.extend(["--title", title])
        if body is not None:
            arguments.extend(["--body-file", "-"])
        if len(arguments) == 3:
            return self
        if not repo.in_memory:
            repo.run_gh(*arguments, stdin=body)
        self.title = title if title is not None else self.title
        self.body = body if body is not None else self.body
        return self

    def comment(self, body: str) -> Ticket:
        """Add a comment to this issue."""
        repo = self._require_repo("comment")
        if repo.in_memory:
            repo._ticket_comments.setdefault(self.number, []).append(body)
            return self
        repo.run_gh("issue", "comment", str(self.number), "--body-file", "-", stdin=body)
        return self

    def add_child(self, child: Ticket) -> Ticket:
        """Attach an existing issue as a direct sub-issue of this issue."""
        repo = self._require_repo("add_child")
        if child.number not in self.sub_issue_numbers:
            self.sub_issue_numbers.append(child.number)
        child.parent_number = self.number
        if repo.in_memory:
            children = repo._ticket_children.setdefault(self.number, [])
            if child.number not in children:
                children.append(child.number)
            repo._ticket_parents[child.number] = self.number
            return child
        repo.run_gh(
            "issue",
            "edit",
            str(self.number),
            "--add-sub-issue",
            child.url or str(child.number),
        )
        return child

    def add_label(self, name: str) -> Ticket:
        """Put a label on this issue (sidebar chip). Empty name is a no-op."""
        label = (name or "").strip()
        if not label:
            return self
        repo = self._require_repo("add_label")
        if label not in self.labels:
            self.labels.append(label)
        if repo.in_memory:
            return self
        repo.run_gh("label", "create", label, "--force")
        repo.run_gh("issue", "edit", str(self.number), "--add-label", label)
        return self

    def remove_label(self, name: str) -> Ticket:
        """Take a label off this issue. Empty or absent name is a quiet no-op."""
        label = (name or "").strip()
        if not label:
            return self
        repo = self._require_repo("remove_label")
        if label in self.labels:
            self.labels.remove(label)
        if repo.in_memory:
            return self
        repo.run_gh("issue", "edit", str(self.number), "--remove-label", label)
        return self

    def add_theme(self, theme: str) -> Ticket:
        """Apply theme on the issue label and the project board Theme field."""
        self.add_label(issue_theme_label(theme))
        return self.write_project_theme(theme)

    def write_project_theme(self, theme: str) -> Ticket:
        """Write the GitHub project board Theme single-select field for this issue."""
        slug = theme_slug(theme)
        if not slug:
            return self
        repo = self._require_repo("write_project_theme")
        project = repo.project
        if project is None:
            return self
        if repo.in_memory:
            repo._ticket_project_theme[self.number] = slug
            return self
        project.write_theme(self.project_item_id(project), slug)
        return self

    def project_item_id(self, project: Project) -> str:
        try:
            return project.item_id_for(self.number)
        except ValueError:
            logger.info("adding missing project item for issue %s", self.number)
        item_id = project.add_item(self.url)
        if not item_id:
            raise GhConnectError("Could not add issue to project.")
        return item_id

    def write_type(self, name: str) -> Ticket:
        """Apply a GitHub issue Type name (org type). Mapping lives on WorkTicket."""
        text = (name or "").strip()
        if not text:
            return self
        self.issue_type = text
        repo = self._require_repo("write_type")
        if repo.in_memory:
            return self
        repo.run_gh("issue", "edit", str(self.number), "--type", text)
        return self

    def set_status(self, state_name: str) -> Ticket:
        repo = self._require_repo("set_status")
        project = repo.project
        if project is None:
            raise RuntimeError("attach_project before setting ticket status")
        state = project.state_named(state_name)
        if repo.in_memory:
            repo._ticket_project_state[self.number] = state.name
            self.state = state
            return self
        resolved = project.write_status(self.project_item_id(project), state.name)
        self.state = project.state_named(resolved)
        return self

    @classmethod
    def from_number(cls, ref: str | int) -> int:
        if isinstance(ref, int):
            return ref
        cleaned = str(ref).strip()
        if not cleaned:
            raise ValueError(f"not a GitHub issue reference: {ref!r}")
        if cleaned.startswith("#"):
            return int(cleaned[1:])
        if "#" in cleaned:
            suffix = cleaned.rsplit("#", 1)[-1]
            if _ISSUE_NUMBER.match(suffix):
                return int(suffix)
        if "/issues/" in cleaned:
            suffix = cleaned.rstrip("/").split("/")[-1]
            if _ISSUE_NUMBER.match(suffix):
                return int(suffix)
        if _ISSUE_NUMBER.match(cleaned):
            return int(cleaned)
        raise ValueError(f"not a GitHub issue reference: {ref!r}")

    @classmethod
    def github_ref(cls, owner: str, repo: str, number: int) -> str:
        return f"{owner}/{repo}#{number}"


@dataclass
class CliAgentBinding:
    """Doer/judge CLI on a session branch — status and pids live on a git tag."""

    status: str = "closed"
    doer: str = ""
    doer_pid: int = 0
    judge: str = ""
    judge_pid: int = 0

    @property
    def open(self) -> bool:
        return self.status == "open" and self.pid_is_alive(self.doer_pid)

    def message(self) -> str:
        return Commit.note_text(
            {
                "status": self.status,
                "doer": self.doer,
                "doer_pid": str(self.doer_pid or ""),
                "judge": self.judge,
                "judge_pid": str(self.judge_pid or ""),
            }
        )

    @classmethod
    def from_message(cls, text: str) -> CliAgentBinding:
        data = Commit(sha="", message=text).note_payload()
        binding = cls()
        return cls(
            status=(data.get("status") or "closed").strip() or "closed",
            doer=(data.get("doer") or "").strip(),
            doer_pid=binding._as_pid(data.get("doer_pid")),
            judge=(data.get("judge") or "").strip(),
            judge_pid=binding._as_pid(data.get("judge_pid")),
        )

    def pid_is_alive(self, pid: int) -> bool:
        if pid <= 0:
            return False
        if os.name == "nt":
            return self._windows_pid_is_alive(pid)
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    def _windows_pid_is_alive(self, pid: int) -> bool:
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000, 0, int(pid))
        if not handle:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True

    def _as_pid(self, raw: str | None) -> int:
        text = (raw or "").strip()
        if not text.isdigit():
            return 0
        return int(text)

    def write_tag(self, repo: Repo, branch_name: str) -> None:
        repo._annotated_tag_target = branch_name
        repo.write_annotated_tag(
            repo.cli_agent_tag_name(branch_name),
            self.message(),
        )


class Project:
    """GitHub Project board on a repo — owns ticket states."""

    __slots__ = ("_repo", "owner", "number", "states", "text_field_name")

    def __init__(self, repo: Repo, owner: str, number: int) -> None:
        self._repo = repo
        self.owner = owner
        self.number = number
        self.states = [TicketState(name) for name in DEFAULT_PROJECT_STATES]
        self.text_field_name = "Ultimate Parent"

    def refresh_states(self) -> list[str]:
        """Load Status column names from GitHub and replace the in-memory state list."""
        names = self.status_option_names()
        if names:
            self.states = [TicketState(name) for name in names]
        return names

    def state_named(self, name: str) -> TicketState:
        options = self.status_option_names()
        resolved = self.github_status_option(name, options)
        candidates = options or [state.name for state in self.states]
        for state_name in candidates:
            if state_name.lower() == resolved.lower():
                return TicketState(state_name)
        raise ValueError(
            f"unknown project state: {name!r}; board columns: {candidates}"
        )

    def status_option_names(self) -> list[str]:
        """Live GitHub Status field option names, or empty when listing fails."""
        if self._repo.in_memory:
            return [state.name for state in self.states]
        try:
            payload = self._field_list_payload()
        except GhConnectError as exc:
            raise self._project_scope_error(exc) from exc
        return self._option_names_for_field("Status", payload)

    def ticket_rows(self) -> list[dict[str, str | int]]:
        """Return project issues with their board status."""
        if self._repo.in_memory:
            return self._memory_ticket_rows()
        raw = self._repo.run_gh(
            "project",
            "item-list",
            str(self.number),
            "--owner",
            self.owner,
            "--limit",
            "1000",
            "--format",
            "json",
        )
        payload = json.loads(raw or "{}")
        return self._ticket_rows_from_items(payload.get("items") or [])

    def write_status(self, item_id: str, state_name: str) -> str:
        """Write the Status column for one item; returns the GitHub option name sent."""
        field_id, options = self._single_select_field("Status")
        option_names = [str(option.get("name") or "") for option in options]
        gh_value = self.github_status_option(state_name, option_names)
        option_id = self._option_id_for_name(options, gh_value)
        self._edit_single_select(item_id, (field_id, option_id))
        return gh_value

    def write_theme(self, item_id: str, theme_slug: str) -> str:
        """Write the Theme column for one item; returns the GitHub option name sent."""
        field_id, options = self._single_select_field("Theme")
        option_names = [str(option.get("name") or "") for option in options]
        gh_value = self.github_theme_option(theme_slug, option_names)
        option_id = self._option_id_for_name(options, gh_value)
        self._edit_single_select(item_id, (field_id, option_id))
        return gh_value

    @classmethod
    def github_status_option(
        cls, state_name: str, option_names: list[str] | tuple[str, ...] | None = None
    ) -> str:
        """Pick a Status option: exact match first, then a known synonym."""
        wanted = (state_name or "").strip()
        names = [str(item).strip() for item in (option_names or ()) if str(item).strip()]
        if wanted in names:
            return wanted
        aliases = GITHUB_STATUS_ALIASES.get(wanted, ())
        for alias in aliases:
            if not names or alias in names:
                return alias
        return wanted

    @classmethod
    def github_theme_option(
        cls, theme: str, option_names: list[str] | tuple[str, ...] | None = None
    ) -> str:
        """Pick a project Theme option matching the slug (case-insensitive)."""
        wanted = theme_slug(theme)
        if not wanted:
            return ""
        names = [str(item).strip() for item in (option_names or ()) if str(item).strip()]
        if wanted in names:
            return wanted
        lower = wanted.lower()
        for name in names:
            if name.lower() == lower:
                return name
        return wanted

    def write_text_field(self, ticket_number: int, value: str) -> None:
        """Write this project's text field on one issue's project item."""
        if self._repo.in_memory:
            self._repo._ticket_project_fields.setdefault(ticket_number, {})[
                self.text_field_name
            ] = value
            return
        field_id = self._ensure_text_field(self.text_field_name)
        item_id = self.item_id_for(ticket_number)
        project_id = self._project_id()
        self._repo.run_gh(
            "project",
            "item-edit",
            "--id",
            item_id,
            "--project-id",
            project_id,
            "--field-id",
            field_id,
            "--text",
            value,
        )

    def _edit_single_select(self, item_id: str, field_option: tuple[str, str]) -> None:
        field_id, option_id = field_option
        self._repo.run_gh(
            "project",
            "item-edit",
            "--id",
            item_id,
            "--project-id",
            self._project_id(),
            "--field-id",
            field_id,
            "--single-select-option-id",
            option_id,
        )

    def archive_ticket(self, ticket_number: int) -> None:
        """Archive an issue's project item without deleting the issue."""
        if self._repo.in_memory:
            self._repo._archived_project_tickets.add(ticket_number)
            return
        self._repo.run_gh(
            "project",
            "item-archive",
            str(self.number),
            "--owner",
            self.owner,
            "--id",
            self.item_id_for(ticket_number),
        )

    def _project_id(self) -> str:
        raw = self._repo.run_gh(
            "project",
            "view",
            str(self.number),
            "--owner",
            self.owner,
            "--format",
            "json",
        )
        project_id = str(json.loads(raw or "{}").get("id") or "")
        if not project_id:
            raise ValueError(f"project {self.owner}/{self.number} has no id")
        return project_id

    def _field_rows(self) -> list[dict[str, object]]:
        raw = self._repo.run_gh(
            "project",
            "field-list",
            str(self.number),
            "--owner",
            self.owner,
            "--format",
            "json",
        )
        payload = json.loads(raw or "{}")
        return [row for row in payload.get("fields") or [] if isinstance(row, dict)]

    def _single_select_field(self, field_name: str) -> tuple[str, list[dict[str, object]]]:
        for field in self._field_rows():
            if str(field.get("name") or "") != field_name:
                continue
            field_id = str(field.get("id") or "")
            options = [
                option
                for option in (field.get("options") or [])
                if isinstance(option, dict)
            ]
            if not field_id:
                raise ValueError(f"project field has no id: {field_name}")
            return field_id, options
        raise ValueError(f"project field not found: {field_name}")

    def _option_id_for_name(
        self, field_options: list[dict[str, object]], name: str
    ) -> str:
        wanted = (name or "").strip()
        for option in field_options:
            label = str(option.get("name") or "").strip()
            if label == wanted or label.lower() == wanted.lower():
                option_id = str(option.get("id") or "")
                if option_id:
                    return option_id
        raise ValueError(f"unknown project option: {name!r}")

    def add_item(self, url: str) -> str:
        item_raw = self._repo.run_gh(
            "project",
            "item-add",
            str(self.number),
            "--owner",
            self.owner,
            "--url",
            url,
            "--format",
            "json",
        )
        item = json.loads(item_raw or "{}")
        return str(item.get("id") or "")

    def _ensure_text_field(self, field_name: str) -> str:
        for field in self._field_rows():
            if str(field.get("name") or "") == field_name:
                return str(field.get("id") or "")
        raw = self._repo.run_gh(
            "project",
            "field-create",
            str(self.number),
            "--owner",
            self.owner,
            "--name",
            field_name,
            "--data-type",
            "TEXT",
            "--format",
            "json",
        )
        field_id = str(json.loads(raw or "{}").get("id") or "")
        if not field_id:
            raise ValueError(f"project field was not created: {field_name}")
        return field_id

    def item_id_for(self, number: int) -> str:
        raw = self._repo.run_gh(
            "project",
            "item-list",
            str(self.number),
            "--owner",
            self.owner,
            "--limit",
            "1000",
            "--format",
            "json",
        )
        for item in json.loads(raw or "{}").get("items") or []:
            content = item.get("content") if isinstance(item, dict) else None
            if isinstance(content, dict) and content.get("number") == number:
                return str(item.get("id") or "")
        raise ValueError(f"ticket {number} is not on the project board")

    def _memory_ticket_rows(self) -> list[dict[str, str | int]]:
        rows: list[dict[str, str | int]] = []
        for number, ticket in self._repo.tickets.items():
            status = self._repo._ticket_project_state.get(number, "")
            if not status:
                continue
            rows.append(
                {
                    "number": number,
                    "title": ticket.title,
                    "url": ticket.url,
                    "status": status,
                }
            )
        return rows

    def _ticket_rows_from_items(
        self, items: list[dict[str, object]]
    ) -> list[dict[str, str | int]]:
        rows: list[dict[str, str | int]] = []
        for item in items:
            content = item.get("content")
            if not isinstance(content, dict) or content.get("type") != "Issue":
                continue
            rows.append(
                {
                    "number": int(content.get("number") or 0),
                    "title": str(content.get("title") or item.get("title") or ""),
                    "url": str(content.get("url") or ""),
                    "status": str(item.get("status") or ""),
                }
            )
        return rows

    def theme_option_names(self) -> list[str]:
        """Live GitHub Theme field option names, or empty when listing fails."""
        if self._repo.in_memory:
            return ["cli-agent", "workspace", "workflow", "tools"]
        try:
            payload = self._field_list_payload()
        except GhConnectError:
            return []
        return self._option_names_for_field("Theme", payload)

    def _field_list_payload(self) -> object:
        raw = self._repo.run_gh(
            "project",
            "field-list",
            str(self.number),
            "--owner",
            self.owner,
            "--format",
            "json",
        )
        return json.loads(raw or "{}")

    def _option_names_for_field(self, field_name: str, payload: object) -> list[str]:
        fields = payload
        if isinstance(payload, dict):
            fields = payload.get("fields") or payload.get("items") or []
        names: list[str] = []
        for field in fields or []:
            names.extend(self._labels_from_field(field, field_name))
        return names

    def _labels_from_field(self, field: object, field_name: str) -> list[str]:
        if not isinstance(field, dict):
            return []
        if str(field.get("name") or "") != field_name:
            return []
        names: list[str] = []
        for option in field.get("options") or []:
            if isinstance(option, dict):
                label = str(option.get("name") or "").strip()
            else:
                label = str(option).strip()
            if label:
                names.append(label)
        return names

    def _project_scope_error(self, exc: GhConnectError) -> GhConnectError:
        message = str(exc)
        if "read:project" in message or "missing required scopes" in message:
            return GhConnectError(f"{message} {GH_PROJECT_SCOPES_HINT}")
        return exc

    def link_repository(self) -> None:
        """Attach this org project to the current GitHub repository."""
        repo = self._repo
        owner, name = repo.owner_repo()
        if repo.in_memory:
            repo._project_links.append((self.owner, self.number, f"{owner}/{name}"))
            return
        repo.run_gh(
            "project",
            "link",
            str(self.number),
            "--owner",
            self.owner,
            "--repo",
            f"{owner}/{name}",
        )


@agent_toolset
class Repo:
    """Local git clone with optional GitHub project + tickets."""

    NOTES_REF = "refs/notes/eval-mistakes"

    def __init__(
        self,
        root: str | Path = ".",
        *,
        memory: bool = False,
        owner: str = "",
        repo_name: str = "",
    ) -> None:
        self.root = Path(root).resolve()
        self.default_branch = "main"
        self._memory = memory
        self._owner = owner
        self._repo_name = repo_name
        self._project: Project | None = None
        self._tickets: dict[int, Ticket] = {}
        self._ticket_project_state: dict[int, str] = {}
        self._ticket_project_theme: dict[int, str] = {}
        self._ticket_project_fields: dict[int, dict[str, str]] = {}
        self._ticket_children: dict[int, list[int]] = {}
        self._ticket_parents: dict[int, int] = {}
        self._ticket_comments: dict[int, list[str]] = {}
        self._closed_tickets: set[int] = set()
        self._archived_project_tickets: set[int] = set()
        self._annotated_tag_target = "HEAD"
        self._agent_active: Repo | None = None
        if memory:
            self._init_memory_state()

    @property
    def in_memory(self) -> bool:
        return self._memory

    @property
    def tickets(self) -> dict[int, Ticket]:
        return dict(self._tickets)

    def has_ticket(self, number: int) -> bool:
        return number in self._tickets

    def mark_closed(self, number: int) -> None:
        self._closed_tickets.add(number)

    def find_root(self) -> Path | None:
        current = self.root
        if current.is_file():
            current = current.parent
        for candidate in (current, *current.parents):
            if (candidate / ".git").exists():
                return candidate
        return None

    @classmethod
    def open(cls, start: str | Path) -> Repo:
        root = cls(start).find_root()
        if root is None:
            raise RepoConnectError(f"not a git clone: {start!r}")
        return cls(root)

    @classmethod
    def memory(cls, root: str | Path = ".", *, owner: str = "demo-org", repo_name: str = "demo-repo") -> Repo:
        return cls(root, memory=True, owner=owner, repo_name=repo_name)

    @classmethod
    def git(cls, root: str | Path, *args: str, env: dict[str, str] | None = None, timeout: float | None = None) -> str:
        """Run git in ``root``. ``env`` adds variables to git's environment; ``timeout`` overrides the default limit."""
        found = shutil.which("git")
        if not found:
            for candidate in (
                Path(r"C:\Program Files\Git\cmd\git.exe"),
                Path(r"C:\Program Files\Git\bin\git.exe"),
            ):
                if candidate.is_file():
                    found = str(candidate)
                    break
        if not found:
            raise RepoConnectError("Cannot connect git: `git` is not available.")
        timeout = timeout or (
            _NETWORK_COMMAND_TIMEOUT_SECONDS
            if args and args[0] in _NETWORK_COMMANDS
            else _COMMAND_TIMEOUT_SECONDS
        )
        try:
            returncode, stdout, stderr = cls._run_git_process(
                [found, "-c", "core.longpaths=true", "-C", str(root), *args], timeout, env
            )
        except subprocess.TimeoutExpired as exc:
            raise RepoConnectError(
                f"Cannot connect git: git {' '.join(args)} exceeded "
                f"{timeout} seconds in {root}."
            ) from exc
        except OSError as exc:
            raise RepoConnectError(f"Cannot connect git: {exc}.") from exc
        if returncode != 0:
            err = (stderr or stdout or "").strip()
            raise RepoConnectError(
                f"Cannot connect git: git {' '.join(args)} failed in {root}: "
                f"{err}."
            )
        return (stdout or "").strip()

    @classmethod
    def _run_git_process(cls, argv: list[str], timeout: float, env: dict[str, str] | None = None) -> tuple[int, str, str]:
        process = subprocess.Popen(
            argv,
            env={**os.environ, **env} if env else None,
            # Under the MCP stdio host, an inherited stdin pipe can hang git on Windows.
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            cls._kill_process_tree(process)
            process.communicate()
            raise
        return process.returncode, stdout, stderr

    @classmethod
    def _kill_process_tree(cls, process: subprocess.Popen) -> None:
        # Git for Windows' cmd\git.exe is a launcher; killing only the launcher leaves the real
        # git holding the output pipes, so communicate() would block long past the timeout.
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(process.pid)],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                check=False,
            )
            return
        process.kill()

    @classmethod
    def gh(
        cls,
        *args: str,
        cwd: str | Path | None = None,
        stdin: str | None = None,
    ) -> str:
        found = shutil.which("gh")
        if not found:
            for candidate in (
                Path(r"C:\Program Files\GitHub CLI\gh.exe"),
                Path.home() / "AppData" / "Local" / "GitHub CLI" / "gh.exe",
            ):
                if candidate.is_file():
                    found = str(candidate)
                    break
        if not found:
            raise GhConnectError("Cannot connect gh: `gh` is not available.")
        try:
            completed = subprocess.run(
                [found, *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                cwd=str(cwd) if cwd is not None else None,
                input=stdin,
                timeout=_COMMAND_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            shown = " ".join(a for a in args if a != stdin)
            raise GhConnectError(
                f"Cannot connect gh: gh {shown} exceeded {_COMMAND_TIMEOUT_SECONDS} seconds."
            ) from exc
        except OSError as exc:
            raise GhConnectError(f"Cannot connect gh: {exc}.") from exc
        if completed.returncode != 0:
            err = (completed.stderr or completed.stdout or "").strip()
            shown = " ".join(a for a in args if a != stdin)
            raise GhConnectError(
                f"Cannot connect gh: gh {shown} failed: {err}."
            )
        return (completed.stdout or "").strip()

    def run_gh(self, *args: str, stdin: str | None = None) -> str:
        return type(self).gh(*args, cwd=self.root, stdin=stdin)

    def _git(self, *args: str) -> str:
        return type(self).git(self.root, *args)

    def _gh(self, *args: str, stdin: str | None = None) -> str:
        return self.run_gh(*args, stdin=stdin)

    def _init_memory_state(self) -> None:
        self._branch_names: set[str] = {"main"}
        self._branch = "main"
        self._commit = "sha-init"
        self._commits: list[tuple[list[str], str]] = []
        self._pushes: list[str] = []
        self._deleted: list[str] = []
        self._dirty = False
        self._notes: dict[str, dict[str, str]] = {}
        self._project_links: list[tuple[str, int, str]] = []
        self._org_issue_types: list[dict[str, str]] = []
        self._worktrees: list[Worktree] = [Worktree(self.root, "main")]
        self._fetches: list[str] = []
        self._pulls: list[str] = []
        self._stash = False
        self._annotated_tags: dict[str, str] = {}
        self._notes_by_ref: dict[tuple[str, str], dict[str, str]] = {}

    @property
    def project(self) -> Project | None:
        return self._project

    def attach_project(self, owner: str, number: int) -> Project:
        self._project = Project(self, owner, number)
        self._project.link_repository()
        self._project.refresh_states()
        return self._project

    def branch_named(self, name: str) -> Branch:
        return Branch(self, name)

    def cli_agent_tag_name(self, branch: str) -> str:
        slug = (branch or "").strip() or "HEAD"
        return f"cli-agent/{slug}"

    def read_cli_agent_tag(self, branch: str) -> CliAgentBinding:
        return CliAgentBinding.from_message(
            self.read_annotated_tag(self.cli_agent_tag_name(branch))
        )

    def write_annotated_tag(self, name: str, message: str) -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("annotated tag requires a name")
        if self._memory:
            self._annotated_tags[name] = message
            return
        self._git("tag", "-f", "-a", name, "-m", message, self._annotated_tag_target)

    def read_annotated_tag(self, name: str) -> str:
        name = (name or "").strip()
        if not name:
            return ""
        if self._memory:
            return self._annotated_tags.get(name, "")
        try:
            return self._git("tag", "-l", "--format=%(contents)", name)
        except RepoConnectError:
            return ""

    def list_annotated_tags(self, prefix: str = "") -> dict[str, str]:
        prefix = prefix or ""
        if self._memory:
            return {
                name: text
                for name, text in self._annotated_tags.items()
                if name.startswith(prefix)
            }
        try:
            listing = self._git("tag", "-l", f"{prefix}*") if prefix else self._git("tag", "-l")
        except RepoConnectError:
            return {}
        return {
            name: self.read_annotated_tag(name)
            for name in listing.splitlines()
            if name.strip()
        }

    @property
    def current_branch(self) -> str:
        if self._agent_active is not None:
            return self._agent_active.current_branch
        if self._memory:
            return self._branch
        return self._git("rev-parse", "--abbrev-ref", "HEAD")

    @current_branch.setter
    def current_branch(self, name: str) -> None:
        if self.is_dirty() and name != self.current_branch:
            raise DirtyBranchSwitchError(self.current_branch, name)
        if self._memory:
            if name not in self._branch_names:
                raise RepoConnectError(f"unknown branch {name}")
            self._branch = name
            return
        self._git( "checkout", name)

    @property
    def current_commit(self) -> str:
        if self._memory:
            return self._commit
        return self._git("rev-parse", "HEAD")

    def list_issue_types(self) -> list[dict[str, str]]:
        if self._memory:
            return [dict(item) for item in getattr(self, "_org_issue_types", [])]
        owner, _ = self.owner_repo()
        raw = self._gh("api", f"orgs/{owner}/issue-types")
        payload = json.loads(raw or "[]")
        return [dict(item) for item in payload] if isinstance(payload, list) else []

    def ensure_issue_type(
        self,
        name: str,
        *,
        description: str = "",
        color: str = "gray",
    ) -> str:
        wanted = (name or "").strip()
        if not wanted:
            return ""
        for item in self.list_issue_types():
            existing = str(item.get("name") or "").strip()
            if existing.lower() == wanted.lower():
                return existing
        record = {
            "name": wanted,
            "description": description,
            "color": color,
            "is_enabled": True,
        }
        if self._memory:
            types = getattr(self, "_org_issue_types", None)
            if types is None:
                self._org_issue_types = []
                types = self._org_issue_types
            types.append(record)
            return wanted
        owner, _ = self.owner_repo()
        self._gh(
            "api",
            "--method",
            "POST",
            f"orgs/{owner}/issue-types",
            "--input",
            "-",
            stdin=json.dumps(
                {
                    "name": wanted,
                    "is_enabled": True,
                    "description": description or None,
                    "color": color,
                }
            ),
        )
        return wanted

    def owner_repo(self) -> tuple[str, str]:
        if self._memory:
            return self._owner, self._repo_name
        raw = self._gh("repo", "view", "--json", "nameWithOwner")
        payload = json.loads(raw or "{}")
        name = payload.get("nameWithOwner", "")
        if "/" not in name:
            raise GhConnectError(f"Cannot resolve owner/repo for {self.root}.")
        owner, repo = name.split("/", 1)
        return owner, repo

    def is_dirty(
        self, path: str | Path | None = None, *, untracked: bool = True
    ) -> bool:
        if self._memory:
            return self._dirty
        args = [
            "status",
            "--porcelain",
            "--untracked-files=normal" if untracked else "--untracked-files=no",
        ]
        if path is not None:
            args.extend(["--", self._rel(path)])
        return any(
            not self._is_runtime_log(line)
            for line in self._git(*args).splitlines()
            if line.strip()
        )

    @staticmethod
    def _is_runtime_log(porcelain_line: str) -> bool:
        raw = porcelain_line[3:] if len(porcelain_line) >= 3 else porcelain_line
        name = raw.split(" -> ")[-1].replace("\\", "/").strip()
        return Path(name).name == "events.log"

    def mark_dirty(self, dirty: bool = True) -> None:
        if not self._memory:
            raise RuntimeError("mark_dirty is only supported on Repo.memory()")
        self._dirty = dirty

    def create_branch(self, name: str) -> None:
        if self._memory:
            self._branch_names.add(name)
            return
        self._git("branch", name)

    def checkout_or_create(self, name: str) -> str:
        if self.current_branch == name:
            return name
        if self.is_dirty():
            raise DirtyBranchSwitchError(self.current_branch, name)
        if self._memory:
            self._branch_names.add(name)
            self._branch = name
            return name
        existing = self._git( "branch", "--list", name)
        if existing:
            self._git( "checkout", name)
        else:
            self._git( "checkout", "-b", name)
        return name

    def commit(
        self, paths: list[str], message: str, *, untracked: bool = False
    ) -> str:
        if not paths:
            raise ValueError("commit requires at least one path")
        if self._memory:
            self._commits.append((list(paths), message))
            self._commit = f"commit-{len(self._commits)}"
            self._dirty = False
            return self._commit
        merge_in_progress = (self.root / ".git" / "MERGE_HEAD").is_file()
        if merge_in_progress:
            add_flag = "-A" if untracked else "-u"
            self._git("add", add_flag)
            staged = self._git("diff", "--cached", "--name-only")
            if not staged:
                return self.current_commit
            self._git("commit", "-m", message)
            return self.current_commit
        rels = [self._rel(path) for path in paths]
        add_flag = "-A" if untracked else "-u"
        self._git("add", add_flag, "--", *rels)
        staged = self._git("diff", "--cached", "--name-only", "--", *rels)
        if not staged:
            return self.current_commit
        self._git("commit", "-m", message, "--", *rels)
        return self.current_commit

    def push_upstream(self) -> None:
        if self._memory:
            self._pushes.append(self.current_branch)
            return
        self._git( "push", "-u", "origin", self.current_branch)

    def has_unpushed_commits(self) -> bool:
        if self._memory:
            return False
        try:
            count = self._git("rev-list", "@{upstream}..HEAD", "--count").strip()
            return int(count or "0") > 0
        except RepoConnectError:
            return False

    def needs_push(self) -> bool:
        """True when the current branch has no upstream yet or is ahead of it."""
        if self._memory:
            return True
        if not self._ref_exists(f"refs/remotes/origin/{self.current_branch}"):
            return True
        return self.has_unpushed_commits()

    def checkout_from_default(self, name: str) -> str:
        """Check out ``name``; a missing branch starts from origin's copy, else from the default branch."""
        if self._memory:
            self._branch_names.add(name)
            self._branch = name
            return name
        if self._ref_exists(f"refs/heads/{name}"):
            self._git("checkout", name)
            return name
        self._git("checkout", "-b", name, self._branch_start_point(name))
        return name

    def delete_branch(self, name: str) -> None:
        """Delete merged branch ``name`` here and on origin."""
        if self._memory:
            self._branch_names.discard(name)
            self._deleted.append(name)
            return
        self._git("branch", "-d", name)
        if self._ref_exists(f"refs/remotes/origin/{name}"):
            self._git("push", "origin", "--delete", name)

    def _branch_start_point(self, name: str) -> str:
        if self._ref_exists(f"refs/remotes/origin/{name}"):
            return f"origin/{name}"
        return self._worktree_start_point() or self.default_branch

    def list_worktrees(self) -> list[Worktree]:
        if self._memory:
            return list(self._worktrees)
        trees: list[Worktree] = []
        path = ""
        branch = ""
        for line in self._git("worktree", "list", "--porcelain").splitlines():
            path, branch, trees = self._accumulate_worktree_line(
                line, path, branch, trees
            )
        return self._flush_worktree(
            Worktree(Path(path), branch) if path else None, trees
        )

    def _accumulate_worktree_line(
        self,
        line: str,
        path: str,
        branch: str,
        trees: list[Worktree],
    ) -> tuple[str, str, list[Worktree]]:
        if line.startswith("worktree "):
            return (
                line[len("worktree ") :],
                "",
                self._flush_worktree(
                    Worktree(Path(path), branch) if path else None, trees
                ),
            )
        if line.startswith("branch "):
            return path, self._branch_from_porcelain(line), trees
        if line == "":
            return (
                "",
                "",
                self._flush_worktree(
                    Worktree(Path(path), branch) if path else None, trees
                ),
            )
        return path, branch, trees

    def _branch_from_porcelain(self, line: str) -> str:
        ref = line[len("branch ") :]
        if ref.startswith("refs/heads/"):
            return ref[len("refs/heads/") :]
        return ref

    def _flush_worktree(
        self, tree: Worktree | None, trees: list[Worktree]
    ) -> list[Worktree]:
        if tree is None:
            return trees
        return trees + [tree]

    def worktree_for(self, branch: str) -> Worktree | None:
        wanted = (branch or "").strip()
        for tree in self.list_worktrees():
            if tree.branch == wanted:
                return tree
        return None

    def add_worktree(self, path: str | Path, branch: str) -> Path:
        dest = Path(path)
        existing = self.worktree_for(branch)
        if existing is not None:
            return existing.path
        if self._memory:
            self._branch_names.add(branch)
            self._worktrees.append(Worktree(dest, branch))
            return dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        if self._ref_exists(f"refs/heads/{branch}"):
            self._git("worktree", "add", str(dest), branch)
        else:
            self._git("worktree", "add", "-b", branch, str(dest), self._branch_start_point(branch))
        return dest.resolve()

    def remove_worktree(self, path: str | Path) -> None:
        dest = Path(path)
        if self._memory:
            self._worktrees = [tree for tree in self._worktrees if tree.path != dest]
            return
        try:
            self._git("worktree", "remove", "--force", str(dest))
        except RepoConnectError as exc:
            logger.info("worktree remove failed; forcing directory delete: %s", exc)
            self._force_remove_directory_windows(dest)
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        if dest.exists():
            self._force_remove_directory_windows(dest)
        if dest.exists():
            return
        try:
            self._git("worktree", "prune")
        except RepoConnectError as exc:
            logger.info("worktree prune failed: %s", exc)

    def _force_remove_directory_windows(self, path: Path) -> bool:
        """Last resort when git/shutil cannot delete a locked checkout (Windows only)."""
        if os.name != "nt":
            return False
        target = path.resolve()
        if not target.exists():
            return True
        user = os.environ.get("USERNAME", "").strip()
        if not user:
            return False
        self._take_windows_ownership(target, user)
        self._rmtree_logged(target)
        if target.exists():
            self._powershell_remove_item(target)
        return not target.exists()

    def _take_windows_ownership(self, target: Path, user: str) -> None:
        for args in (
            ("takeown", "/f", str(target), "/r", "/d", "y"),
            ("icacls", str(target), "/grant", f"{user}:(F)", "/t"),
        ):
            try:
                subprocess.run(list(args), capture_output=True, check=False)
            except OSError as exc:
                logger.info("windows ownership command failed: %s", exc)

    def _rmtree_logged(self, target: Path) -> None:
        try:
            shutil.rmtree(target, ignore_errors=True)
        except OSError as exc:
            logger.info("rmtree failed for %s: %s", target, exc)

    def _powershell_remove_item(self, target: Path) -> None:
        try:
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    (
                        f'Remove-Item -LiteralPath "{target}" '
                        "-Recurse -Force -ErrorAction SilentlyContinue"
                    ),
                ],
                capture_output=True,
                check=False,
            )
        except OSError as exc:
            logger.info("powershell Remove-Item failed for %s: %s", target, exc)

    def fetch(self) -> None:
        if self._memory:
            self._fetches.append("origin")
            return
        self._git("fetch", "origin")

    def pull(self) -> None:
        if self._memory:
            self._pulls.append(self.current_branch)
            return
        self._git("pull", "--ff-only")

    def fetch_pull(self) -> None:
        self.fetch()
        self.pull()

    def merge_from(self, other: str, message: str = "") -> str:
        """Merge *other* into the current branch without checking *other* out."""
        if not other or other == self.current_branch:
            return self.current_commit
        if self._memory:
            text = message or f"merge {other} into {self.current_branch}"
            self._commits.append(([], text))
            self._commit = f"merge-{other}-into-{self.current_branch}"
            return self._commit
        if message:
            self._git("merge", other, "-m", message)
        else:
            self._git("merge", other, "--no-edit")
        return self.current_commit

    def push_to(self, branch: str) -> None:
        if self._memory:
            self._pushes.append(branch)
            return
        self._git("push", "origin", f"HEAD:{branch}")

    def has_stash(self) -> bool:
        if self._memory:
            return self._stash
        return bool(self._git("stash", "list"))

    def clear_stash(self) -> None:
        """Drop every stash entry. Session close must not leave worktrees for stash."""
        if self._memory:
            self._stash = False
            return
        if not self.has_stash():
            return
        self._git("stash", "clear")

    def is_linked_worktree(self) -> bool:
        return (self.root / ".git").is_file()

    def primary_root(self) -> Path:
        if self._memory:
            return self.root
        common = Path(self._git("rev-parse", "--git-common-dir"))
        if not common.is_absolute():
            common = (self.root / common).resolve()
        else:
            common = common.resolve()
        return common.parent if common.name == ".git" else common

    def _ref_exists(self, ref: str) -> bool:
        try:
            self._git("show-ref", "--verify", "--quiet", ref)
            return True
        except RepoConnectError:
            return False

    def _worktree_start_point(self) -> str:
        for candidate in (
            f"origin/{self.default_branch}",
            "origin/main",
            "origin/master",
        ):
            try:
                self._git("rev-parse", "--verify", candidate)
                return candidate
            except RepoConnectError:
                continue
        return ""

    def merge_branch(self, source: str, into: str = "main", message: str = "") -> str:
        if self.is_dirty(untracked=False):
            raise DirtyBranchSwitchError(self.current_branch, into)
        if self._memory:
            if source not in self._branch_names:
                self._branch_names.add(source)
            self._branch = into
            text = message or f"merge {source} into {into}"
            self._commits.append(([], text))
            self._commit = f"merge-{source}-into-{into}"
            return self._commit
        target = self.worktree_for(into)
        merge_root = Path(target.path) if target is not None else Path(self.root)
        if target is None and self.current_branch != into:
            self._git("checkout", into)
            merge_root = Path(self.root)
        merge_git = type(self)
        if message:
            merge_git.git(merge_root, "merge", source, "-m", message)
        else:
            merge_git.git(merge_root, "merge", source, "--no-edit")
        return merge_git.git(merge_root, "rev-parse", "HEAD")

    def note(
        self,
        sha: str,
        payload: dict[str, str],
        *,
        ref: str | None = None,
    ) -> None:
        note_ref = ref or self.NOTES_REF
        if self._memory:
            self._notes[sha] = dict(payload)
            self._notes_by_ref[(note_ref, sha)] = dict(payload)
            return
        text = Commit.note_text(payload)
        self._git(
            "notes",
            f"--ref={note_ref}",
            "add",
            "-f",
            "-m",
            text,
            sha,
        )

    def read_notes(self, sha: str, *, ref: str | None = None) -> dict[str, str]:
        note_ref = ref or self.NOTES_REF
        if self._memory:
            keyed = self._notes_by_ref.get((note_ref, sha))
            if keyed is not None:
                return dict(keyed)
            if note_ref == self.NOTES_REF:
                return dict(self._notes.get(sha, {}))
            return {}
        try:
            raw = self._git("notes", f"--ref={note_ref}", "show", sha)
        except RepoConnectError:
            return {}
        return Commit(sha="", message=raw).note_payload()

    def find_mistakes(
        self, entry_ids: list[str], *, ref: str | None = None
    ) -> list[dict[str, str]]:
        note_ref = ref or self.NOTES_REF
        wanted = set(entry_ids)
        if self._memory:
            return self._memory_mistakes(wanted)
        return self._listed_mistakes(note_ref, wanted)

    def _memory_mistakes(self, wanted: set[str]) -> list[dict[str, str]]:
        found: list[dict[str, str]] = []
        for sha, payload in self._notes.items():
            if payload.get("entry_id") in wanted:
                row = dict(payload)
                row.setdefault("introducing_commit", sha)
                found.append(row)
        return found

    def _listed_mistakes(
        self, note_ref: str, wanted: set[str]
    ) -> list[dict[str, str]]:
        found: list[dict[str, str]] = []
        listing = self._git("notes", f"--ref={note_ref}", "list")
        for line in listing.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            sha = parts[1]
            payload = self.read_notes(sha, ref=note_ref)
            if payload.get("entry_id") in wanted:
                payload.setdefault("introducing_commit", sha)
                found.append(payload)
        return found

    def ticket(self, ref: str) -> Ticket | None:
        if self.in_memory:
            return self._memory_ticket(ref)
        return self._github_ticket(ref)

    def _memory_ticket(self, ref: str) -> Ticket | None:
        number = Ticket.from_number(ref)
        ticket = self._tickets.get(number)
        if ticket is None:
            return None
        ticket.bind_repo(self)
        state_name = self._ticket_project_state.get(number)
        if state_name:
            ticket.state = TicketState(state_name)
        ticket.data["closed"] = "true" if number in self._closed_tickets else "false"
        ticket.sub_issue_numbers = list(self._ticket_children.get(number, []))
        ticket.parent_number = self._ticket_parents.get(number)
        return ticket

    def _github_ticket(self, ref: str) -> Ticket | None:
        number = Ticket.from_number(ref)
        try:
            raw = self.run_gh(
                "issue",
                "view",
                str(number),
                "--json",
                "number,title,body,url,state,parent,subIssues",
            )
        except GhConnectError as exc:
            message = str(exc).lower()
            if "could not resolve" in message or "not found" in message:
                return None
            raise
        payload = json.loads(raw or "{}")
        if not payload:
            return None
        return self._ticket_from_payload(payload)

    def create_ticket(self, title: str, body: str) -> Ticket:
        if self.in_memory:
            number = (max(self._tickets.keys(), default=0) + 1) if self._tickets else 1
            owner, repo_name = self.owner_repo()
            ticket = Ticket(
                number=number,
                title=title,
                body=body,
                url=f"https://github.com/{owner}/{repo_name}/issues/{number}",
            )
            ticket.bind_repo(self)
            self._tickets[number] = ticket
            return ticket
        raw = self.run_gh(
            "issue",
            "create",
            "--title",
            title,
            "--body-file",
            "-",
            stdin=body,
        )
        url = (raw or "").strip().splitlines()[-1].strip() if raw else ""
        if "/issues/" not in url:
            raise GhConnectError(f"Cannot parse issue URL from gh issue create: {raw!r}.")
        number = int(url.rstrip("/").rsplit("/", 1)[-1])
        ticket = self.ticket(str(number))
        if ticket is None:
            return self._ticket_from_payload(
                {"number": number, "title": title, "body": body, "url": url}
            )
        ticket.body = body
        ticket.title = title
        return ticket

    def workflow_commit_message(
        self,
        subject: str,
        issue_number: int,
        workflow_state: str,
        *,
        reviewed_by: str = "",
    ) -> str:
        owner, repo = self.owner_repo()
        trailers = {
            "GitHub-Issue": Ticket.github_ref(owner, repo, issue_number),
            "Workflow-State": workflow_state,
        }
        if reviewed_by.strip():
            trailers["Reviewed-By"] = reviewed_by.strip()
        return Commit.format(subject, trailers)

    def _ticket_from_payload(self, payload: dict[str, Any]) -> Ticket:
        number = int(payload["number"])
        parent_data = payload.get("parent")
        parent_number = (
            int(parent_data["number"])
            if isinstance(parent_data, dict) and parent_data.get("number")
            else None
        )
        sub_issues_data = payload.get("subIssues") or []
        if isinstance(sub_issues_data, dict):
            sub_issues_data = sub_issues_data.get("nodes") or []
        sub_numbers = [
            int(item["number"])
            for item in sub_issues_data
            if isinstance(item, dict) and item.get("number")
        ]
        ticket = Ticket(
            number=number,
            title=str(payload.get("title") or ""),
            body=str(payload.get("body") or ""),
            url=str(payload.get("url") or ""),
            parent_number=parent_number,
            sub_issue_numbers=sub_numbers,
        )
        ticket.bind_repo(self)
        self._tickets[number] = ticket
        return ticket

    def _last_commit_message(self) -> str:
        if self._memory:
            if not self._commits:
                return ""
            return self._commits[-1][1]
        return self._git("log", "-1", "--pretty=%B")

    def _rel(self, path: str | Path) -> str:
        resolved = Path(path).resolve()
        try:
            return str(resolved.relative_to(self.root)).replace("\\", "/")
        except ValueError:
            return str(resolved).replace("\\", "/")

    @property
    def commits(self) -> list[tuple[list[str], str]]:
        if not self._memory:
            raise RuntimeError("commits is only available on Repo.memory()")
        return self._commits

    @property
    def pushes(self) -> list[str]:
        if not self._memory:
            raise RuntimeError("pushes is only available on Repo.memory()")
        return self._pushes

    @property
    def _branches(self) -> set[str]:
        if not self._memory:
            raise RuntimeError("_branches is only available on Repo.memory()")
        return self._branch_names

    @property
    def checkout_path(self) -> str:
        return str(self._agent_repo().root)

    def _agent_repo(self) -> Repo:
        if self._agent_active is not None:
            return self._agent_active
        if self._memory or self.find_root() is not None:
            return self
        return Worktree.open(self.root).repository

    def _bind(self, repository: Repo) -> Repo:
        self._agent_active = repository
        return repository

    def _primary_repo(self) -> Repo:
        """The main clone; branch commands never act inside a linked worktree."""
        repository = self._agent_repo()
        if repository.in_memory or not repository.is_linked_worktree():
            return repository
        return Repo(repository.primary_root())

    def _work_state(self) -> WorkState:
        return WorkState(self._primary_repo().root)

    def _at(self, repo_path: str) -> Repo | None:
        """The clone at ``repo_path`` when it names one other than this toolset's; else None."""
        if not (repo_path or "").strip():
            return None
        target = Repo.open(repo_path)
        if not self._memory and target.root == self.find_root():
            return None
        return target

    def _branch_name(self, name: str) -> str:
        cleaned = (name or "").strip() or self._work_state().branch
        if not cleaned:
            raise BranchNameRequiredError()
        return cleaned

    @agent_tool
    @mcp
    def switch_branch(self, name: str = "", repo_path: str = "") -> str:
        """Switch the main clone to branch ``name``, creating it when missing.

        ``repo_path`` names the project's clone; omit it to act on the clone the tools started in.
        ``name`` defaults to ``branch`` in ``.sessions/session.json``. Commits the branch being
        left and pushes it (the default branch is committed but not pushed), checks out
        ``name`` (a new branch starts from origin's copy or the default branch), and saves
        ``name`` as ``branch`` in ``.sessions/session.json``. Does not touch worktrees or sessions.
        """
        other = self._at(repo_path)
        if other is not None:
            return other.switch_branch(name)
        wanted = self._branch_name(name)
        repository = self._primary_repo()
        if repository.current_branch != wanted:
            repository.branch_named(repository.current_branch).save(f"branch: switch to {wanted}")
            repository.checkout_from_default(wanted)
        self._work_state().branch = wanted
        return f"on branch {wanted!r} at {repository.root}"

    @agent_tool
    @mcp
    def close_branch(self, name: str = "", commit_message: str = "branch: close", repo_path: str = "") -> str:
        """Close branch ``name``: commit, push, merge into the default branch, push it, delete ``name``.

        ``repo_path`` names the project's clone; omit it to act on the clone the tools started in.
        ``name`` defaults to ``branch`` in ``.sessions/session.json``. Refuses the default branch and
        a branch still open in a worktree. Deletes ``name`` locally and on origin, leaves the main
        clone on the default branch, and saves the default branch as ``branch``. Does not touch sessions.
        The release that landed (the open session, else ``name``) keeps its end-to-end results, its
        screenshots pushed to ``e2e-latest``; every older release's results are removed and that removal is
        committed and pushed on the default branch.
        """
        other = self._at(repo_path)
        if other is not None:
            return other.close_branch(name, commit_message)
        wanted = self._branch_name(name)
        repository = self._primary_repo()
        default = repository.default_branch
        if wanted == default:
            raise DefaultBranchError("close", default)
        occupied = repository.worktree_for(wanted)
        if occupied is not None and Path(occupied.path).resolve() != Path(repository.root).resolve():
            raise BranchInWorktreeError(wanted, Path(occupied.path))
        release = self._work_state().session or wanted
        self.switch_branch(wanted)
        repository.branch_named(wanted).close(commit_message)
        self._work_state().branch = default
        pruned = [] if repository.in_memory else LatestRelease(repository, release).keep()
        kept = f"; kept {release!r} end-to-end results, removed {', '.join(pruned)}" if pruned else ""
        return f"closed branch {wanted!r}: merged into {default!r}, pushed, and deleted{kept}"

    @agent_tool
    @mcp
    def switch_worktree(self, name: str = "", repo_path: str = "") -> str:
        """Open the sibling worktree for branch ``name``, creating the branch and folder when missing.

        ``repo_path`` names the project's clone; omit it to act on the clone the tools started in.
        ``name`` defaults to ``branch`` in ``.sessions/session.json`` and must not be the default
        branch. When the main clone has ``name`` checked out, it is committed, pushed, and the main
        clone goes back to the default branch so the worktree can take it. Saves ``branch`` and the
        worktree path as ``worktree`` in ``.sessions/session.json``; later repo tools act in it.
        """
        other = self._at(repo_path)
        if other is not None:
            return other.switch_worktree(name)
        wanted = self._branch_name(name)
        primary = self._primary_repo()
        if wanted == primary.default_branch:
            raise DefaultBranchError("open a worktree for", primary.default_branch)
        if primary.current_branch == wanted:
            primary.branch_named(wanted).save(f"worktree: move {wanted} to its worktree")
            primary.checkout_from_default(primary.default_branch)
        opened = self._bind(primary.branch_named(wanted).open_in_worktree())
        state = WorkState(primary.root)
        state.branch = wanted
        state.worktree = str(opened.root)
        return f"worktree for {wanted!r} at {opened.root}"

    @agent_tool
    @mcp
    def close_worktree(self, commit_message: str = "worktree: close", repo_path: str = "") -> str:
        """Close the worktree saved in ``.sessions/session.json``: commit, push its branch, remove the folder.

        ``repo_path`` names the project's clone; omit it to act on the clone the tools started in.
        Does not merge; the branch stays open as ``branch``. Clears ``worktree`` in
        ``.sessions/session.json`` and returns later repo tools to the main clone.
        """
        other = self._at(repo_path)
        if other is not None:
            return other.close_worktree(commit_message)
        state = self._work_state()
        if not state.worktree:
            raise NoOpenWorktreeError()
        tree = Repo(state.worktree)
        branch = tree.current_branch
        tree.branch_named(branch).save(commit_message)
        Repo(tree.primary_root()).remove_worktree(tree.root)
        state.worktree = ""
        self._agent_active = None
        return f"closed worktree for {branch!r}; branch pushed and kept open"

    @command(name="switch-branch")
    @agent_instructions
    def switch_branch_command(self) -> str:
        """Switch the main clone to a branch, creating it when missing.

        Use the branch the user names; otherwise call without a name so the branch saved in
        ``.sessions/session.json`` is used. Pass ``repo_path`` as the project's clone (``CDD_PROJECT``, else the current working directory). Call MCP ``repo.switch_branch``."""
        return ""

    @command(name="close-branch")
    @agent_instructions
    def close_branch_command(self) -> str:
        """Close a branch: commit, push, merge into main, push main, delete the branch.

        Use the branch the user names; otherwise call without a name so the branch saved in
        ``.sessions/session.json`` is used. Pass ``repo_path`` as the project's clone (``CDD_PROJECT``, else the current working directory). Call MCP ``repo.close_branch``."""
        return ""

    @command(name="switch-worktree")
    @agent_instructions
    def switch_worktree_command(self) -> str:
        """Open the sibling worktree for a branch other than main, creating it when missing.

        Use the branch the user names; otherwise call without a name so the branch saved in
        ``.sessions/session.json`` is used. Pass ``repo_path`` as the project's clone (``CDD_PROJECT``, else the current working directory). Call MCP ``repo.switch_worktree``."""
        return ""

    @command(name="close-worktree")
    @agent_instructions
    def close_worktree_command(self) -> str:
        """Close the open worktree: commit, push its branch, remove the folder. The branch stays open.

        Pass ``repo_path`` as the project's clone (``CDD_PROJECT``, else the current working directory). Call MCP ``repo.close_worktree``."""
        return ""

    @agent_tool
    @mcp
    def push_commit(
        self,
        message: str,
        *,
        untracked: bool = True,
        sync_remote: bool = True,
        repo_path: str = "",
    ) -> Commit:
        """Commit the working tree using ``message`` (subject and optional body).

        ``repo_path`` names the checkout to commit; omit it to commit the one the tools act in."""
        other = self._at(repo_path)
        repository = other._agent_repo() if other is not None else self._agent_repo()
        text = (message or "").strip()
        if not text:
            raise ValueError("commit message is required")
        sha = repository.commit(
            [str(repository.root)], text, untracked=untracked
        )
        if sync_remote and not repository._memory:
            repository.push_upstream()
        return Commit.from_message(sha, text)

    @command(name="push")
    @agent_instructions
    def push(self, hint: str = "") -> str:
        """Commit local changes. Optional hint: {{hint}}.

        Inspect git status and diff (staged and unstaged) with the Shell tool.
        On Windows PowerShell, chain git commands with ``;`` (``&&`` is not supported).

        Draft a commit message that:
        - Summarizes what changed and why in a short imperative subject.
        - Names practice, fidelity, and artifact format when this session used CDD
          tools (slash commands, MCP tools, or skills), for example bdd-behavior,
          clean-engineering-code, or sketch.
        - Calls out key paths when that clarifies scope.

        If the working tree is clean, say so and do not call ``repo.push_commit``.
        Otherwise call MCP ``repo.push_commit`` with the full message (subject plus body when useful)
        and ``repo_path`` set to the project's checkout (``CDD_PROJECT``, else the current working directory).
        """
        return ""


class Worktree:
    """One checkout (path + branch) and git worktree / in-clone operations."""

    __slots__ = ("path", "branch", "_repository")

    def __init__(
        self,
        path_or_repo: Path | str | Repo,
        branch: str = "",
    ) -> None:
        if isinstance(path_or_repo, Repo):
            self._repository = path_or_repo
            self.path = Path(path_or_repo.root)
            self.branch = (path_or_repo.current_branch or "").strip()
        else:
            self.path = Path(path_or_repo)
            self.branch = (branch or "").strip()
            self._repository = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Worktree):
            return NotImplemented
        return self.path == other.path and self.branch == other.branch

    def __repr__(self) -> str:
        return f"Worktree(path={self.path!r}, branch={self.branch!r})"

    def _repo(self) -> Repo:
        if self._repository is not None:
            return self._repository
        return Repo(self.path)

    @property
    def repository(self) -> Repo:
        return self._repo()

    @classmethod
    def open(cls, path: str | Path = "") -> Worktree:
        raw = str(path or ".").strip() or "."
        found = Repo(raw).find_root()
        if found is None:
            raise RepoConnectError("repo tools require a git repository")
        return cls(Repo(found))

    @staticmethod
    def cursor_path(worktree_id: str) -> Path:
        """Detached checkout under ``~/.cursor/worktrees/{worktree_id}``."""
        slug = (worktree_id or "").strip()
        if not slug:
            raise ValueError("worktree id is required")
        return Path.home() / ".cursor" / "worktrees" / slug

    @staticmethod
    def abbrev_repo_name(folder: str) -> str:
        tokens = [part for part in re.split(r"[-_]+", folder or "") if part]
        if not tokens:
            return folder or "repo"
        if len(tokens) == 1:
            return tokens[0]
        return tokens[0] + "-" + "".join(token[0] for token in tokens[1:])

    @staticmethod
    def dirname(repo_folder: str, branch: str) -> str:
        """Sibling directory ``{abbrev}-{short-branch}`` next to the primary clone."""
        slug = (branch or "").strip().replace("/", "-")
        ticket = re.search(r"-(\d+)$", slug)
        short = ticket.group(1) if ticket else slug
        if ticket is None and len(short) > 24:
            short = short[:24].rstrip("-")
        return f"{Worktree.abbrev_repo_name(repo_folder)}-{short}"

    def fetch_pull(self) -> None:
        repository = self._repo()
        try:
            repository.fetch()
        except RepoConnectError:
            return
        try:
            repository.pull()
        except RepoConnectError:
            return


class Branch:
    """Named branch on a *Repo* — checkout, commit, merge, and close."""

    __slots__ = ("_repo", "name")

    def __init__(self, repo: Repo, name: str) -> None:
        self._repo = repo
        self.name = (name or "").strip()

    @property
    def repo(self) -> Repo:
        return self._repo

    def checkout(self) -> Branch:
        self._repo.checkout_or_create(self.name)
        return self

    def open_in_worktree(self) -> Repo:
        """Check out this branch in a sibling worktree and return that clone."""
        repository = self._repo
        if getattr(repository, "_memory", False):
            self.checkout()
            return repository
        existing = repository.worktree_for(self.name)
        if existing is not None and existing.path.resolve() != Path(repository.root).resolve():
            other = Repo(existing.path)
            Worktree(other).fetch_pull()
            return other
        if repository.current_branch == self.name:
            Worktree(repository).fetch_pull()
            return repository
        try:
            repository.fetch()
        except RepoConnectError:
            pass
        primary = repository.primary_root()
        dest = primary.parent / Worktree.dirname(primary.name, self.name)
        tree_path = repository.add_worktree(dest, self.name)
        other = Repo(tree_path)
        Worktree(other).fetch_pull()
        return other

    def cli_agent(self) -> CliAgentBinding:
        return self._repo.read_cli_agent_tag(self.name)

    @property
    def head(self) -> Commit:
        from space.repo.repo import Commit

        return Commit.from_message(
            self._repo.current_commit,
            self._repo._last_commit_message(),
        )

    def commit(self, paths: list[str], message: str) -> Commit:
        from space.repo.repo import Commit

        sha = self._repo.commit(paths, message)
        return Commit.from_message(sha, message)

    def merge(self, other: Branch, *, message: str = "") -> Commit:
        from space.repo.repo import Commit

        sha = self._repo.merge_branch(other.name, self.name, message=message)
        return Commit.from_message(sha, message or f"merge {other.name} into {self.name}")

    def save(self, commit_message: str) -> None:
        """Commit every change on this checked-out branch, then push it when origin is behind.

        The default branch is committed locally but never pushed here; closing a branch pushes it.
        """
        repository = self._repo
        if repository.is_dirty():
            repository.commit([str(repository.root)], commit_message, untracked=True)
        if self.name != repository.default_branch and repository.needs_push():
            repository.push_upstream()

    def land_on_default(self) -> None:
        """Merge this branch into the default branch on this clone and push the default branch."""
        repository = self._repo
        default = repository.default_branch
        repository.checkout_from_default(default)
        repository.pull()
        repository.merge_from(self.name, message=f"merge {self.name} into {default}")
        repository.push_upstream()

    def close(self, commit_message: str = "branch: close") -> None:
        """Save this checked-out branch, land it on the default branch, then delete it here and on origin."""
        self.save(commit_message)
        self.land_on_default()
        self._repo.delete_branch(self.name)
